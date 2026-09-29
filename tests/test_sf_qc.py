import json

from fixtures import make_story, prepare_media
import sf_captions
import sf_qc
import sf_render
from sflib.project import ROOT, load_story, save_story

SMALL = (360, 640)
STYLES = ROOT / "config" / "caption-styles"


def _rendered(tmp_path):
    project = prepare_media(tmp_path, make_story(), [1000, 700, 1300])
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    return project


def test_clean_render_passes_every_check(tmp_path):
    project = _rendered(tmp_path)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 0, summary
    report = json.loads((project / "out/qc.json").read_text())
    assert [c["name"] for c in report["checks"]] == [
        "assets_done", "frames_match", "audio_duration", "resolution", "caption_timing", "caption_line_length", "silence"]
    assert all(c["ok"] for c in report["checks"])
    assert report["approx_ratio"] == 1.0
    assert load_story(project)["output"]["qc"] == "out/qc.json"


def test_stale_render_fails_frame_and_duration_checks(tmp_path):
    project = _rendered(tmp_path)
    story = load_story(project)
    story["lines"][0]["audio"]["duration_ms"] += 500
    save_story(project, story)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2
    assert "frames_match" in summary["failed"] and "audio_duration" in summary["failed"]


def test_overlapping_cues_fail_caption_timing(tmp_path):
    project = _rendered(tmp_path)
    ass = project / "out/captions.ass"
    # prepare_media durations [1000, 700, 1300] put L003 at 1950–3250 ms; pull its cue back over L001's
    ass.write_text(ass.read_text().replace("0:00:01.95,0:00:03.25", "0:00:00.50,0:00:03.25"), encoding="utf-8")
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2 and summary["failed"] == ["caption_timing"]


def test_missing_audio_fails_gracefully_without_a_timeline(tmp_path):
    project = prepare_media(tmp_path, make_story(), [1000, 700, 1300])
    story = load_story(project)
    story["lines"][0]["audio"]["status"] = "pending"
    story["lines"][0]["audio"]["duration_ms"] = None
    save_story(project, story)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2
    assert "assets_done" in summary["failed"]
    report = json.loads((project / "out/qc.json").read_text())
    assert [c["name"] for c in report["checks"]] == [
        "assets_done", "frames_match", "audio_duration", "resolution", "caption_timing", "caption_line_length", "silence"]
    assert load_story(project)["output"]["qc"] == "out/qc.json"


def test_cue_past_its_own_line_fails_caption_timing(tmp_path):
    project = _rendered(tmp_path)
    ass = project / "out/captions.ass"
    # L001 ends at 1000 ms; L002 starts at 1250 ms, so this cue overlaps nothing and ends before the video does
    ass.write_text(ass.read_text().replace("0:00:00.00,0:00:01.00", "0:00:00.00,0:00:01.20"), encoding="utf-8")
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2 and summary["failed"] == ["caption_timing"]
    report = json.loads((project / "out/qc.json").read_text())
    assert "L001" in next(c["detail"] for c in report["checks"] if c["name"] == "caption_timing")


def _wav_with_inline_gap(project, line_id, lead_ms, gap_ms, trail_ms):
    import io
    import wave
    from fixtures import sine_wav_bytes
    with wave.open(io.BytesIO(sine_wav_bytes(lead_ms))) as tone:
        lead = tone.readframes(tone.getnframes())
    with wave.open(io.BytesIO(sine_wav_bytes(trail_ms))) as tone:
        trail = tone.readframes(tone.getnframes())
    silence = b"\x00\x00" * round(24000 * gap_ms / 1000)
    with wave.open(str(project / f"audio/{line_id}.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(lead + silence + trail)


def test_inline_silence_within_a_lines_pause_tag_allowance_passes(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = "Every single. [pause 300ms] night."
    project = prepare_media(tmp_path, story, [1000, 1700, 1300])
    _wav_with_inline_gap(project, "L002", 500, 700, 500)  # 500 + 700 + 500 = 1700ms, matches duration_ms
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 0, summary


def test_inline_silence_without_a_pause_tag_fails(tmp_path):
    story = make_story()  # L002's text has no [pause] tag
    project = prepare_media(tmp_path, story, [1000, 1700, 1300])
    _wav_with_inline_gap(project, "L002", 500, 700, 500)  # same 0.7s in-line gap as above
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2 and summary["failed"] == ["silence"]


def test_inline_silence_at_a_sentence_break_within_allowance_passes(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = "Every single. Night falls quick."  # two sentences, no [pause] tag
    project = prepare_media(tmp_path, story, [1000, 1960, 1300])
    _wav_with_inline_gap(project, "L002", 500, 960, 500)  # 0.96s, as measured on real OmniVoice output
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 0, summary


def test_inline_silence_at_the_same_gap_fails_for_a_single_clause_line(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = "Every single night falling quick."  # one clause, same 0.96s gap
    project = prepare_media(tmp_path, story, [1000, 1960, 1300])
    _wav_with_inline_gap(project, "L002", 500, 960, 500)
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2 and summary["failed"] == ["silence"]


def test_inline_silence_past_the_sentence_pause_allowance_still_fails(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = "Every single. Night falls quick."  # two sentences
    project = prepare_media(tmp_path, story, [1000, 2500, 1300])
    _wav_with_inline_gap(project, "L002", 500, 1500, 500)  # over SENTENCE_PAUSE_S + SILENCE_GRACE_S (1.3s)
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2 and summary["failed"] == ["silence"]


def test_inline_silence_after_a_closing_quote_widens_the_allowance(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = 'Co het "Doi da!" roi bo di.'  # closing quote right after the "!"
    project = prepare_media(tmp_path, story, [1000, 1960, 1300])
    _wav_with_inline_gap(project, "L002", 500, 960, 500)
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 0, summary


def test_inline_silence_before_a_trailing_quote_does_not_widen_the_allowance(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = 'Co het "Doi da roi!"'  # sentence-ending punctuation + quote at the very end
    project = prepare_media(tmp_path, story, [1000, 1960, 1300])
    _wav_with_inline_gap(project, "L002", 500, 960, 500)
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2 and summary["failed"] == ["silence"]


def test_silence_straddling_a_lines_end_uses_its_pause_after_ms(tmp_path):
    import io
    import wave
    from fixtures import sine_wav_bytes
    story = make_story()
    story["lines"][0]["pause_after_ms"] = 300  # so pause_after_ms + 0.1s (0.4s) clearly beats the 0.3s grace alone
    project = prepare_media(tmp_path, story, [1000, 700, 1300])
    # L001's own 50ms-trim residue: its last 40ms are silent, i.e. the gap starts 40ms before its own end.
    with wave.open(io.BytesIO(sine_wav_bytes(960))) as tone:
        lead = tone.readframes(tone.getnframes())
    with wave.open(str(project / "audio/L001.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(lead + b"\x00\x00" * round(24000 * 40 / 1000))
    # L002's own leading trim residue: 60ms of silence before its tone starts.
    # Combined: 40ms (L001 tail) + 300ms (real pause_after_ms) + 60ms (L002 head) = 400ms = pause_after_ms + 0.1s,
    # straddling L001's end -- it must be judged as L001's inter-line gap, not an in-line silence.
    with wave.open(io.BytesIO(sine_wav_bytes(640))) as tone:
        rest = tone.readframes(tone.getnframes())
    with wave.open(str(project / "audio/L002.wav"), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(b"\x00\x00" * round(24000 * 60 / 1000) + rest)
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 0, summary


def test_silence_is_measured_against_its_own_lines_pause(tmp_path):
    import io
    import wave
    from fixtures import sine_wav_bytes
    project = prepare_media(tmp_path, make_story(), [1000, 1000, 1300])
    with wave.open(io.BytesIO(sine_wav_bytes(400))) as tone:
        frames = tone.readframes(tone.getnframes())
    with wave.open(str(project / "audio/L002.wav"), "wb") as wav:  # L002 (pause 0) goes quiet for its last 600 ms
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(frames + b"\x00\x00" * 14400)
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2 and summary["failed"] == ["silence"]
