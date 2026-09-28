from fixtures import make_story, write_project
import sf_align
from sflib.project import load_story, save_story
from sflib.text import tokens


def _w(text, start, end):
    return {"text": text, "start": start, "end": end}


def _times(words):
    return [(w["text"], w["start_ms"], w["end_ms"], w["approx"]) for w in words]


def test_exact_match_takes_asr_times():
    asr = [_w("Every", 0.0, 0.3), _w("night", 0.3, 0.6), _w("for", 0.6, 0.8), _w("eleven", 0.8, 1.2), _w("years.", 1.2, 1.5)]
    words = sf_align.align_line(["Every", "night", "for", "eleven", "years."], asr, 1500, "en")
    assert _times(words) == [("Every", 0, 300, False), ("night", 300, 600, False), ("for", 600, 800, False),
                             ("eleven", 800, 1200, False), ("years.", 1200, 1500, False)]


def test_substitution_of_equal_length_maps_pairwise():
    asr = [_w("The", 0.0, 0.2), _w("color", 0.2, 0.6), _w("red", 0.6, 0.9)]
    words = sf_align.align_line(["The", "colour", "red"], asr, 900, "en")
    assert _times(words)[1] == ("colour", 200, 600, False)


def test_missing_word_is_interpolated_and_flagged():
    asr = [_w("I", 0.0, 0.2), _w("know", 0.6, 0.9)]
    words = sf_align.align_line(["I", "really", "know"], asr, 900, "en")
    assert _times(words) == [("I", 0, 200, False), ("really", 200, 600, True), ("know", 600, 900, False)]


def test_no_asr_falls_back_to_length_weighted_split():
    words = sf_align.align_line(["ab", "abcd"], [], 600, "en")
    assert _times(words) == [("ab", 0, 200, True), ("abcd", 200, 600, True)]


def test_cluster_language_splits_asr_words():
    asr = [_w("你好", 0.0, 0.4), _w("世界", 0.5, 0.9)]
    words = sf_align.align_line(tokens("你好，世界", "zh"), asr, 900, "zh")
    assert _times(words) == [("你", 0, 200, False), ("好，", 200, 400, False), ("世", 500, 700, False), ("界", 700, 900, False)]


def test_times_are_monotonic_and_clamped():
    asr = [_w("a", 0.5, 0.7), _w("b", 0.2, 0.3), _w("c", 0.9, 5.0)]
    words = sf_align.align_line(["a", "b", "c"], asr, 1000, "en")
    starts = [w["start_ms"] for w in words]
    assert starts == sorted(starts)
    assert all(0 <= w["start_ms"] <= w["end_ms"] <= 1000 for w in words)


def test_run_uses_stored_asr_words_and_skips_when_current(tmp_path):
    story = make_story()
    for line in story["lines"]:
        text_tokens = tokens(line["text"], "en")
        line["audio"].update(status="done", path=f"audio/{line['id']}.wav", duration_ms=1000, input_hash=f"h-{line['id']}",
                             asr_words=[_w(t, i * 0.2, i * 0.2 + 0.2) for i, t in enumerate(text_tokens)])
    project = write_project(tmp_path, story)
    summary, code = sf_align.run(project)
    assert code == 0 and summary["aligned"] == ["L001", "L002", "L003"] and summary["approx_ratio"] == 0.0
    stored = load_story(project)["lines"][2]
    assert [w["text"] for w in stored["words"]] == ["No.", "Not", "again."]
    assert stored["words_hash"] == "h-L003"
    summary, _ = sf_align.run(project)
    assert summary["aligned"] == [] and summary["skipped"] == 3


def test_run_reports_lines_without_audio(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_align.run(project)
    assert code == 2 and summary["needs_human"] == ["L001 has no audio", "L002 has no audio", "L003 has no audio"]


def test_run_handles_auth_error_and_persists_prior_alignments(tmp_path):
    from sflib.project import ProviderError
    story = make_story()
    text_tokens_l1 = tokens(story["lines"][0]["text"], "en")
    text_tokens_l2 = tokens(story["lines"][1]["text"], "en")
    # L001: has stored asr_words (will be aligned without calling client)
    story["lines"][0]["audio"].update(
        status="done", path=f"audio/L001.wav", duration_ms=1000, input_hash="h-L001",
        asr_words=[_w(t, i * 0.2, i * 0.2 + 0.2) for i, t in enumerate(text_tokens_l1)]
    )
    # L002: no asr_words (will trigger client call and fail)
    story["lines"][1]["audio"].update(status="done", path=f"audio/L002.wav", duration_ms=1000, input_hash="h-L002")
    # L003: no audio at all (will skip)
    story["lines"][2]["audio"].update(status="done", duration_ms=0)
    project = write_project(tmp_path, story)

    class FakeClient:
        def transcribe_words(self, path, language):
            raise ProviderError("auth", "nope")

    summary, code = sf_align.run(project, client=FakeClient())
    assert code == 3 and summary["errors"] == ["auth: nope"]
    # Check that L001 was aligned before the failure
    stored = load_story(project)["lines"][0]
    assert [w["text"] for w in stored.get("words", [])] == list(text_tokens_l1)


def test_run_handles_transient_error_with_approx_fallback(tmp_path):
    from sflib.project import ProviderError
    story = make_story()
    # L001: has stored asr_words
    text_tokens_l1 = tokens(story["lines"][0]["text"], "en")
    story["lines"][0]["audio"].update(
        status="done", path=f"audio/L001.wav", duration_ms=1000, input_hash="h-L001",
        asr_words=[_w(t, i * 0.2, i * 0.2 + 0.2) for i, t in enumerate(text_tokens_l1)]
    )
    # L002: triggers transient error (should fallback to approx)
    story["lines"][1]["audio"].update(status="done", path=f"audio/L002.wav", duration_ms=1000, input_hash="h-L002")
    # L003: has audio, no asr_words (to complete the run)
    story["lines"][2]["audio"].update(status="done", path=f"audio/L003.wav", duration_ms=1000, input_hash="h-L003")
    project = write_project(tmp_path, story)

    class FakeClient:
        def __init__(self):
            self.call_count = 0
        def transcribe_words(self, path, language):
            self.call_count += 1
            raise ProviderError("transient", "try again")

    fake = FakeClient()
    summary, code = sf_align.run(project, client=fake)
    # All three lines should align despite transient errors (fallback to approx)
    assert code == 0 and summary["aligned"] == ["L001", "L002", "L003"]
    # L002's words should all be approx=True (fallback to length-weighted split)
    stored = load_story(project)["lines"][1]
    assert all(w["approx"] for w in stored["words"])
