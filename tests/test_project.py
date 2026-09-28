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
