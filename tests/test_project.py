import json

import pytest

from fixtures import make_story, write_project
from sflib.project import (
    LockedError, input_hash, load_config, load_story, needs_work, project_lock, save_story, wanted,
)


def test_save_and_load_roundtrip_leaves_no_temp_files(tmp_path):
    project = write_project(tmp_path, make_story())
    story = load_story(project)
    story["brief"]["idea"] = "Changed — with unicode ✓"
    save_story(project, story)
    assert load_story(project)["brief"]["idea"] == "Changed — with unicode ✓"
    assert [p.name for p in project.iterdir() if p.name.startswith(".story.")] == []


def test_lock_blocks_a_second_holder_and_is_released(tmp_path):
    with project_lock(tmp_path):
        with pytest.raises(LockedError):
            with project_lock(tmp_path):
                pass
    assert not (tmp_path / ".sf.lock").exists()


def test_input_hash_is_stable_and_key_order_independent():
    assert input_hash({"a": 1, "b": [1, 2]}) == input_hash({"b": [1, 2], "a": 1})
    assert input_hash({"a": 1}) != input_hash({"a": 2})
    assert len(input_hash({"a": 1})) == 16


def test_wanted_matches_exact_ids_and_prefixes():
    assert wanted("S01", None)
    assert wanted("S01", {"S01"})
    assert not wanted("S02", {"S01"})
    assert wanted("C01_face", {"C01"})
    assert wanted("C01_face", {"C01_face"})


def test_needs_work(tmp_path):
    (tmp_path / "a.png").write_bytes(b"x")
    done = {"status": "done", "input_hash": "h1", "path": "a.png"}
    assert not needs_work(done, "h1", tmp_path)
    assert needs_work(done, "h2", tmp_path)
    assert needs_work({**done, "path": "missing.png"}, "h1", tmp_path)
    assert needs_work({"status": "pending", "input_hash": None, "path": None}, "h1", tmp_path)
    assert not needs_work({"status": "needs_human", "input_hash": "h1", "path": None}, "h1", tmp_path)
    assert needs_work({"status": "needs_human", "input_hash": "h1", "path": None}, "h2", tmp_path)


def test_load_config_honors_env_override(tmp_path, monkeypatch):
    cfg = tmp_path / "p.yaml"
    cfg.write_text("image:\n  provider: fake\n", encoding="utf-8")
    monkeypatch.setenv("SF_CONFIG", str(cfg))
    assert load_config()["image"]["provider"] == "fake"


def _main(monkeypatch, capsys, argv, run):
    from sflib.project import main_wrapper
    monkeypatch.setattr("sys.argv", ["sf_demo.py", *argv])
    with pytest.raises(SystemExit) as exit_info:
        main_wrapper(run, "demo")
    captured = capsys.readouterr()
    out = captured.out.splitlines()
    assert len(out) == 1
    return exit_info.value.code, json.loads(out[0]), captured.err


def test_main_wrapper_turns_a_crash_into_one_json_line_and_logs_the_traceback(tmp_path, monkeypatch, capsys):
    def run(project_dir, only):
        raise RuntimeError("ffmpeg failed:\nboom")
    code, summary, _ = _main(monkeypatch, capsys, [str(tmp_path)], run)
    assert code == 1 and summary == {"ok": False, "errors": ["RuntimeError: ffmpeg failed:\nboom"]}
    assert "Traceback" in (tmp_path / "logs" / "sf_demo.log").read_text()
    assert not (tmp_path / ".sf.lock").exists()


def test_main_wrapper_reports_a_missing_project_dir(tmp_path, monkeypatch, capsys):
    code, summary, err = _main(monkeypatch, capsys, [str(tmp_path / "nope")], lambda project_dir, only: ({}, 0))
    assert code == 1 and summary["errors"][0].startswith("FileNotFoundError:")
    assert "Traceback" in err and not (tmp_path / "nope").exists()


def test_main_wrapper_appends_one_runs_jsonl_line_per_invocation(tmp_path, monkeypatch, capsys):
    def run(project_dir, only):
        return {"done": ["L001", "L002"], "skipped": 0, "needs_human": []}, 0
    _main(monkeypatch, capsys, [str(tmp_path)], run)
    _main(monkeypatch, capsys, [str(tmp_path)], run)
    lines = (tmp_path / "logs" / "runs.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    entry = json.loads(lines[0])
    assert entry["script"] == "sf_demo" and entry["exit"] == 0
    assert entry["counts"] == {"done": 2, "needs_human": 0}
    assert entry["elapsed_s"] >= 0 and entry["started"].endswith("+00:00")


def test_main_wrapper_records_crashes_but_not_missing_projects(tmp_path, monkeypatch, capsys):
    def boom(project_dir, only):
        raise RuntimeError("x")
    _main(monkeypatch, capsys, [str(tmp_path)], boom)
    entry = json.loads((tmp_path / "logs" / "runs.jsonl").read_text(encoding="utf-8"))
    assert entry["exit"] == 1 and entry["counts"] == {"errors": 1}
    _main(monkeypatch, capsys, [str(tmp_path / "nope")], lambda project_dir, only: ({}, 0))
    assert not (tmp_path / "nope").exists()
