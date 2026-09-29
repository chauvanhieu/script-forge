from fixtures import make_story, write_project
import json
import sf_validate


def _errors(tmp_path, story):
    summary, code = sf_validate.run(write_project(tmp_path, story), root=tmp_path)
    return summary["errors"], code


def test_fixture_story_is_valid(tmp_path):
    errors, code = _errors(tmp_path, make_story())
    assert errors == []
    assert code == 0


def test_schema_error_reports_path(tmp_path):
    story = make_story()
    story["slides"][0]["visual"]["motion"] = "spin"
    errors, code = _errors(tmp_path, story)
    assert code == 2
    assert any(e.startswith("slides/0/visual/motion:") for e in errors)


def test_unknown_speaker_and_character_and_location(tmp_path):
    story = make_story()
    story["lines"][0]["speaker"] = "C09"
    story["slides"][0]["brief"]["characters"] = ["C07"]
    story["slides"][1]["brief"]["location"] = "LOC09"
    errors, _ = _errors(tmp_path, story)
    assert "L001: speaker 'C09' is not in cast" in errors
    assert "S01: character 'C07' is not in cast" in errors
    assert "S02: location 'LOC09' is not in locations" in errors


def test_lines_must_follow_slide_order_exactly(tmp_path):
    story = make_story()
    story["slides"][0]["line_ids"] = ["L002", "L001"]
    errors, _ = _errors(tmp_path, story)
    assert any("line_ids" in e and "lines array order" in e for e in errors)


def test_unsupported_bracket_tag(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = "Every [excited] night."
    errors, _ = _errors(tmp_path, story)
    assert any(e.startswith("L002: unsupported bracket tags") for e in errors)


def test_missing_canon_scene(tmp_path):
    story = make_story()
    project = write_project(tmp_path, story)
    (tmp_path / "stories/demo/scenes/chapter-01-scene-01.md").unlink()
    summary, _ = sf_validate.run(project, root=tmp_path)
    assert "S01: source scene 'chapter-01-scene-01' not found in canon" in summary["errors"]


def test_source_scene_outside_adapted_chapters(tmp_path):
    story = make_story()
    story["slides"][1]["source"] = "chapter-02-scene-01"
    errors, _ = _errors(tmp_path, story)
    assert "S02: source scene 'chapter-02-scene-01' is not in canon.chapters" in errors


def _factual(**research):
    story = make_story(canon=None)
    story["brief"]["content_type"] = "factual"
    for slide in story["slides"]:
        slide["source"] = None
    story["research"] = {
        "notes": [{"id": "R01", "title": "Tide tables", "sources": ["https://example.org/tides"], "status": "verified"}],
        "claims": [
            {"id": "CL01", "text": "High tide comes twice a day here.", "status": "verified", "note_ids": ["R01"]},
            {"id": "CL02", "text": "The light was built in 1851.", "status": "unverified", "note_ids": []},
        ],
        **research,
    }
    return story


def test_factual_claims_must_resolve_and_be_resolved(tmp_path):
    story = _factual()
    story["lines"][0]["claim_ids"] = ["CL01"]
    assert _errors(tmp_path, story)[0] == []
    story["lines"][1]["claim_ids"] = ["CL02", "CL09"]
    errors, code = _errors(tmp_path / "b", story)
    assert code == 2
    assert "L002: claim 'CL09' is not in research.claims" in errors
    assert "L002: claim 'CL02' is unverified; verify it or remove it before Gate 1" in errors


def test_factual_requires_research(tmp_path):
    story = _factual()
    story["research"] = None
    errors, _ = _errors(tmp_path, story)
    assert "factual content requires research" in errors


def test_adaptation_requires_rights_basis(tmp_path):
    story = make_story()
    story["brief"]["content_type"] = "adaptation"
    story["source_work"] = {"title": "The Snow Queen", "author": "H. C. Andersen", "rights_basis": "", "translation_used": None}
    errors, _ = _errors(tmp_path, story)
    assert "adaptation requires source_work.rights_basis" in errors


def test_review_mode_accepts_auto_and_rejects_unknown(tmp_path):
    story = make_story()
    story["brief"]["review_mode"] = "auto"
    assert sf_validate.schema_errors(story) == []
    story["brief"]["review_mode"] = "yolo"
    assert sf_validate.schema_errors(story) != []
