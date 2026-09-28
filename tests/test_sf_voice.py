from fixtures import FakeVS, make_story, write_project
import sf_voice
from sflib.project import load_story

CONFIG = {"voice": {"base_url": "http://vs.local", "engine": None, "qc": {"max_cer": 0.25, "min_cps": 2, "max_cps": 30}}}


def test_cer():
    assert sf_voice.cer("Every night.", "every night") == 0.0
    assert sf_voice.cer("abcd", "abxd") == 0.25
    assert sf_voice.cer("", "") == 0.0


def test_creates_profiles_and_synthesizes_every_line(tmp_path):
    project = write_project(tmp_path, make_story())
    vs = FakeVS()
    summary, code = sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    assert code == 0
    assert summary["profiles"] == ["narrator", "C01"]
    assert summary["done"] == ["L001", "L002", "L003"]
    story = load_story(project)
    assert [c["voice"]["profile_id"] for c in story["cast"]] == ["p1", "p2"]
    audio = story["lines"][0]["audio"]
    assert audio["status"] == "done" and audio["path"] == "audio/L001.wav" and audio["duration_ms"] == 1000
    assert audio["seed"] == sf_voice.default_seed("demo-ch01-916-en", "L001")
    assert audio["qc"]["cer"] == 0.0 and audio["asr_words"][0]["text"] == "Every"
    whisper_call = vs.calls[2]
    assert whisper_call["text"] == "No. [sigh] Not again." and whisper_call["instruct"] == "female, whisper"
    assert vs.calls[0]["instruct"] is None and vs.calls[0]["language"] == "en"


def test_design_profiles_use_speakers_first_spoken_line_as_ref_text(tmp_path):
    project = write_project(tmp_path, make_story())
    vs = FakeVS()
    sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    # narrator's first line is L001, C01's first line is L002 (both plain, no tags)
    assert vs.design_ref_texts == ["Every night for eleven years.", "Every single night."]


def test_design_profile_ref_text_strips_tags_and_shows_written_half(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = "No. [[y'know|you know]] [sigh] fine."
    project = write_project(tmp_path, story)
    vs = FakeVS()
    sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    assert vs.design_ref_texts[1] == "No. y'know fine."


def test_design_profile_ref_text_empty_when_speaker_has_no_spoken_line(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = "[sigh]"
    story["lines"][2]["text"] = "[pause 300ms]"
    project = write_project(tmp_path, story)
    vs = FakeVS()
    sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    assert vs.design_ref_texts == ["Every night for eleven years.", ""]


def test_tag_only_line_reaches_done(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = "[sigh] [pause 300ms]"  # nothing to speak: display text is empty
    project = write_project(tmp_path, story)
    vs = FakeVS()
    summary, code = sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    assert code == 0
    assert summary["done"] == ["L001", "L002", "L003"]
    audio = load_story(project)["lines"][1]["audio"]
    assert audio["status"] == "done" and audio["qc"]["reasons"] == []
    assert audio["qc"]["cps"] is None and audio["qc"]["cer"] is None


def test_take_edges_are_trimmed_before_duration_is_measured(tmp_path):
    project = write_project(tmp_path, make_story())
    # 1000ms tone flanked by 300ms of silence each side; trim_silence's default 50ms pad
    # should shrink that to ~1100ms once the edges are cut.
    vs = FakeVS(padded={"Every night for eleven years.": (300, 300)})
    summary, code = sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    assert code == 0, summary
    audio = load_story(project)["lines"][0]["audio"]
    assert abs(audio["duration_ms"] - 1100) <= 5


def test_second_run_skips_everything(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_voice.run(project, config=CONFIG, client=FakeVS(), root=tmp_path)
    vs = FakeVS()
    summary, code = sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    assert code == 0 and summary["skipped"] == 3 and vs.calls == [] and vs.profiles == 0


def test_failed_qc_retakes_with_a_new_seed(tmp_path):
    project = write_project(tmp_path, make_story())
    vs = FakeVS(bad_transcripts=1)
    summary, code = sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    assert code == 0
    audio = load_story(project)["lines"][0]["audio"]
    assert audio["attempts"] == 2
    assert audio["used_seed"] == audio["seed"] + sf_voice.RETAKE_SEED_STEP


def test_persistent_qc_failure_needs_human(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_voice.run(project, config=CONFIG, client=FakeVS(bad_transcripts=100), root=tmp_path)
    assert code == 2
    audio = load_story(project)["lines"][0]["audio"]
    assert audio["status"] == "needs_human" and audio["attempts"] == 3
    assert "CER" in audio["last_error"]


def test_quota_stops_with_exit_3(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_voice.run(project, config=CONFIG, client=FakeVS(fail_generate="quota"), root=tmp_path)
    assert code == 3 and summary["errors"] == ["quota: refused"]


def test_library_voice_missing_needs_human(tmp_path):
    story = make_story()
    story["cast"][0]["voice"] = {"source": "library", "library_ref": "ghost", "profile_id": None}
    project = write_project(tmp_path, story)
    summary, code = sf_voice.run(project, config=CONFIG, client=FakeVS(), root=tmp_path)
    assert code == 2
    assert any("library voice" in item for item in summary["needs_human"])
    assert "L001" not in summary["done"]


def test_failed_redo_keeps_the_old_take_consistent_with_story(tmp_path):
    from sflib.media import probe_duration_ms
    project = write_project(tmp_path, make_story())
    sf_voice.run(project, config=CONFIG, client=FakeVS(), root=tmp_path)
    vs = FakeVS(bad_transcripts=1, fail_generate="quota", fail_after=1, durations={"Every night for eleven years.": 3000})
    summary, code = sf_voice.run(project, only={"L001"}, config=CONFIG, client=vs, root=tmp_path)
    assert code == 3 and len(vs.calls) == 2
    audio = load_story(project)["lines"][0]["audio"]
    assert probe_duration_ms(project / audio["path"]) == audio["duration_ms"] == 1000
    assert sorted(p.name for p in (project / "audio").iterdir()) == ["L001.wav", "L002.wav", "L003.wav"]


def test_new_audio_invalidates_aligned_words(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_voice.run(project, config=CONFIG, client=FakeVS(), root=tmp_path)
    import sf_align
    sf_align.run(project)
    sf_voice.run(project, only={"L001"}, config=CONFIG, client=FakeVS(), root=tmp_path)
    lines = load_story(project)["lines"]
    assert lines[0]["words"] == [] and lines[0]["words_hash"] is None
    assert lines[1]["words_hash"] == lines[1]["audio"]["input_hash"]


def test_retake_seed_stays_in_int32(tmp_path):
    story = make_story()
    story["lines"][0]["audio"]["seed"] = 2_147_483_646
    project = write_project(tmp_path, story)
    vs = FakeVS(bad_transcripts=1)
    sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    audio = load_story(project)["lines"][0]["audio"]
    assert audio["used_seed"] == (2_147_483_646 + sf_voice.RETAKE_SEED_STEP) % 2_147_483_647
    assert all(0 <= call["seed"] < 2 ** 31 for call in vs.calls)


def test_only_cast_id_recasts_that_voice_and_its_lines(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_voice.run(project, config=CONFIG, client=FakeVS(), root=tmp_path)
    vs = FakeVS()
    vs.profiles = 10
    summary, code = sf_voice.run(project, only={"C01"}, config=CONFIG, client=vs, root=tmp_path)
    assert code == 0 and summary["profiles"] == ["C01"] and summary["done"] == ["L002", "L003"]
    story = load_story(project)
    assert [c["voice"]["profile_id"] for c in story["cast"]] == ["p1", "p11"]
    assert {call["profile_id"] for call in vs.calls} == {"p11"}


def test_clone_voice_with_missing_ref_audio_needs_human(tmp_path):
    story = make_story()
    story["cast"][0]["voice"] = {"source": "clone", "ref_audio": "library/ghost.wav", "ref_text": "hi", "profile_id": None}
    project = write_project(tmp_path, story)
    summary, code = sf_voice.run(project, config=CONFIG, client=FakeVS(), root=tmp_path)
    assert code == 2
    assert any(item.startswith("narrator: reference audio") for item in summary["needs_human"])
    assert summary["done"] == ["L002", "L003"]
