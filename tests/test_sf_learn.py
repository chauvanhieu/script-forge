import json

from fixtures import make_story, write_project
import sf_learn
from sflib.project import load_story, save_story


def _voiced(tmp_path, durations=(1000, 700, 1300)):
    project = write_project(tmp_path / "work", make_story())
    story = load_story(project)
    for line, ms in zip(story["lines"], durations):
        line["audio"].update(status="done", path=f"audio/{line['id']}.wav", duration_ms=ms, input_hash=f"h-{line['id']}")
    save_story(project, story)
    return project


def _log(project, *entries):
    logs = project / "logs"
    logs.mkdir(exist_ok=True)
    with (logs / "runs.jsonl").open("a", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")


VOICE = {"script": "sf_voice", "started": "2026-09-29T10:00:00+00:00", "elapsed_s": 30.0, "exit": 0, "counts": {"done": 3}}
IMAGE = {"script": "sf_image", "started": "2026-09-29T10:01:00+00:00", "elapsed_s": 50.0, "exit": 0, "counts": {"done": 2}}
RENDER = {"script": "sf_render", "started": "2026-09-29T10:02:00+00:00", "elapsed_s": 12.0, "exit": 0, "counts": {"rendered": 2}}


def test_speech_chars_matches_display_text_without_spaces_or_tags():
    assert sf_learn.speech_chars("No. [sigh] Not again.") == len("No.Notagain.")
    assert sf_learn.speech_chars("[sigh]") == 0


def test_first_run_seeds_calibration_and_history(tmp_path):
    project = _voiced(tmp_path)
    _log(project, VOICE, IMAGE, RENDER)
    library = tmp_path / "library"
    summary, code = sf_learn.run(project, library_dir=library)
    assert code == 0 and summary["recorded"] is True
    cal = json.loads((library / "calibration.json").read_text())
    story = load_story(project)
    rates = [sf_learn.speech_chars(l["text"]) / (l["audio"]["duration_ms"] / 1000) for l in story["lines"]]
    assert cal["speaking_rate"]["en"]["lines"] == 3
    assert abs(cal["speaking_rate"]["en"]["chars_per_s"] - sum(rates) / 3) < 1e-6
    assert cal["stage_seconds"]["voice_line"] == {"mean": 10.0, "n": 3}
    assert cal["stage_seconds"]["image"] == {"mean": 25.0, "n": 2}
    assert cal["stage_seconds"]["render"] == {"mean": 12.0, "n": 1}
    history = json.loads((library / "runs" / f"{story['slug']}.json").read_text())
    assert len(history) == 1 and history[0]["run_id"] == summary["run_id"]
    assert history[0]["log_lines"] == 3 and sorted(history[0]["line_hashes"]) == ["h-L001", "h-L002", "h-L003"]
    assert history[0]["voice_lines_generated"] == 3 and history[0]["images_generated"] == 2
    expected_actual = (1000 + 700 + 1300 + sum(l["pause_after_ms"] for l in story["lines"])) / 1000
    assert history[0]["actual_s"] == round(expected_actual, 2)
    assert history[0]["predicted_s"] is None  # no calibration existed before this run


def test_rerun_without_new_log_lines_changes_nothing(tmp_path):
    project = _voiced(tmp_path)
    _log(project, VOICE)
    library = tmp_path / "library"
    sf_learn.run(project, library_dir=library)
    before = (library / "calibration.json").read_text()
    _log(project, {"script": "sf_learn", "started": "x", "elapsed_s": 0.1, "exit": 0, "counts": {}})
    summary, code = sf_learn.run(project, library_dir=library)
    assert code == 0 and summary["recorded"] is False
    assert (library / "calibration.json").read_text() == before


def test_second_run_uses_ewma_and_counts_each_line_hash_once(tmp_path):
    project = _voiced(tmp_path)
    _log(project, VOICE)
    library = tmp_path / "library"
    sf_learn.run(project, library_dir=library)
    old = json.loads((library / "calibration.json").read_text())["speaking_rate"]["en"]["chars_per_s"]
    story = load_story(project)
    story["lines"][0]["audio"].update(duration_ms=2000, input_hash="h-L001-v2")  # one line re-voiced
    save_story(project, story)
    _log(project, dict(VOICE, counts={"done": 1}))
    summary, _ = sf_learn.run(project, library_dir=library)
    cal = json.loads((library / "calibration.json").read_text())
    new_rate = sf_learn.speech_chars(story["lines"][0]["text"]) / 2.0
    assert cal["speaking_rate"]["en"]["lines"] == 4
    assert abs(cal["speaking_rate"]["en"]["chars_per_s"] - ((1 - sf_learn.ALPHA) * old + sf_learn.ALPHA * new_rate)) < 1e-6
    history = json.loads((library / "runs" / f"{story['slug']}.json").read_text())
    assert len(history) == 2 and history[1]["predicted_s"] is not None


def test_no_log_lines_records_nothing(tmp_path):
    project = _voiced(tmp_path)
    summary, code = sf_learn.run(project, library_dir=tmp_path / "library")
    assert code == 0 and summary == {"run_id": None, "recorded": False, "speaking_rate": {}, "library_problems": []}
