from pathlib import Path
import json
import sf_init
import sf_validate


def test_init_creates_valid_story_and_directories(tmp_path):
    project_dir = tmp_path / "projects" / "slug-test"
    summary, code = sf_init.init_project(project_dir, content_type="factual", aspect="9:16", language="vi")
    assert code == 0
    assert summary["ok"] is True
    assert summary["status"] == "initialized"

    for sub in ["audio", "images", "clips", "logs", "out", "prompts"]:
        assert (project_dir / sub).is_dir()

    story_path = project_dir / "story.json"
    assert story_path.exists()
    assert (project_dir / "script.md").exists()

    story = json.loads(story_path.read_text(encoding="utf-8"))
    assert story["slug"] == "slug-test"
    assert story["brief"]["content_type"] == "factual"

    # Validation must pass cleanly
    val_summary, val_code = sf_validate.run(project_dir, root=tmp_path)
    assert val_code == 0
    assert val_summary["errors"] == []


def test_init_does_not_overwrite_without_force(tmp_path):
    project_dir = tmp_path / "projects" / "slug-overwrite"
    sf_init.init_project(project_dir)
    story_path = project_dir / "story.json"
    story = json.loads(story_path.read_text(encoding="utf-8"))
    story["brief"]["idea"] = "Custom Idea Saved"
    story_path.write_text(json.dumps(story), encoding="utf-8")

    # Second call without force
    summary, code = sf_init.init_project(project_dir)
    assert code == 0
    assert summary["status"] == "already_exists"
    loaded = json.loads(story_path.read_text(encoding="utf-8"))
    assert loaded["brief"]["idea"] == "Custom Idea Saved"

    # With force
    summary_force, code_force = sf_init.init_project(project_dir, force=True, idea="Overwritten Idea")
    assert code_force == 0
    assert summary_force["status"] == "initialized"
    loaded_force = json.loads(story_path.read_text(encoding="utf-8"))
    assert loaded_force["brief"]["idea"] == "Overwritten Idea"


def test_init_with_timestamp_prefix_and_seo(tmp_path):
    project_dir = tmp_path / "projects" / "slug-timestamped"
    summary, code = sf_init.init_project(project_dir, content_type="factual", aspect="9:16", language="vi", with_timestamp=True)
    assert code == 0
    assert summary["ok"] is True
    actual_path = Path(summary["project"])
    assert actual_path.exists()
    assert actual_path.name != "slug-timestamped"
    assert "slug-timestamped" in actual_path.name

    story_path = actual_path / "story.json"
    story = json.loads(story_path.read_text(encoding="utf-8"))
    assert "seo" in story
    assert story["seo"]["title"] == "Slug Timestamped"
    assert "keywords" in story["seo"]

    # Must pass schema validation cleanly
    val_summary, val_code = sf_validate.run(actual_path, root=tmp_path)
    assert val_code == 0
    assert val_summary["errors"] == []


def test_init_with_channel(tmp_path):
    project_dir = tmp_path / "projects" / "slug-channel-test"
    summary, code = sf_init.init_project(project_dir, channel="the-grey-verdict", idea="A legal paradox video")
    assert code == 0
    assert summary["ok"] is True

    story_path = project_dir / "story.json"
    story = json.loads(story_path.read_text(encoding="utf-8"))
    assert story["brief"]["channel"] == "the-grey-verdict"
    assert story["seo"]["author"] == "The Grey Verdict"
    assert story["cast"][0]["voice"]["profile_id"] == "6d80d98d"
    assert story["cast"][0]["caption_color"] == "#F5A623"

    # Must pass schema validation cleanly
    val_summary, val_code = sf_validate.run(project_dir, root=tmp_path)
    assert val_code == 0
    assert val_summary["errors"] == []


