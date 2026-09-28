import json
import sys
import textwrap

from PIL import Image

from fixtures import make_story, write_project
import sf_image
from sflib.project import load_story, save_story

FAKE = {"image": {"provider": "fake", "max_refs": 4}}


def _command_config(tmp_path, fail_when: str, error: str) -> dict:
    script = tmp_path / "provider.py"
    script.write_text(textwrap.dedent(f"""
        import json, sys, os
        from PIL import Image
        args = sys.argv[1:]
        out = args[args.index("--out") + 1]
        aspect = args[args.index("--aspect") + 1]
        if {fail_when!r} in os.path.basename(out):
            print(json.dumps({{"error": {error!r}, "message": "refused"}}), file=sys.stderr)
            sys.exit(1)
        sizes = {{"1:1": (64, 64), "3:4": (48, 64), "9:16": (36, 64), "16:9": (64, 36)}}
        Image.new("RGB", sizes[aspect], "gray").save(out)
    """), encoding="utf-8")
    return {"image": {"provider": "command", "command": [sys.executable, str(script)], "timeout_s": 30, "max_refs": 4}}


def test_generates_plates_then_slides_with_correct_sizes(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_image.run(project, config=FAKE)
    assert code == 0
    assert summary["done"] == ["C01_face", "C01_half", "C01_full", "LOC01", "S01", "S02"]
    story = load_story(project)
    face = story["cast"][1]["plates"]["face"]
    assert face["status"] == "done" and face["path"] == "plates/C01_face.png"
    assert Image.open(project / "plates/C01_face.png").size == (1024, 1024)
    assert Image.open(project / "plates/C01_half.png").size == (768, 1024)
    assert Image.open(project / "images/S01.png").size == (1080, 1920)
    assert story["slides"][0]["image"]["attempts"] == 1


def test_second_run_skips_and_prompt_change_regenerates_only_that_slide(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_image.run(project, config=FAKE)
    summary, _ = sf_image.run(project, config=FAKE)
    assert summary["done"] == [] and summary["skipped"] == 6
    story = load_story(project)
    story["slides"][1]["visual"]["prompt"] = "A second light, closer now"
    save_story(project, story)
    summary, _ = sf_image.run(project, config=FAKE)
    assert summary["done"] == ["S02"]


def test_only_forces_regeneration_by_prefix(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_image.run(project, config=FAKE)
    summary, _ = sf_image.run(project, only={"C01"}, config=FAKE)
    assert summary["done"] == ["C01_face", "C01_half", "C01_full"]


def test_content_blocked_face_plate_blocks_its_slides(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_image.run(project, config=_command_config(tmp_path, "_face", "content_blocked"), sleep=lambda s: None)
    assert code == 2
    assert summary["needs_human"] == ["C01_face"]
    assert summary["blocked"] == ["S01 waits for C01_face", "S02 waits for C01_face"]
    face = load_story(project)["cast"][1]["plates"]["face"]
    assert face["status"] == "needs_human" and face["last_error"] == "content_blocked: refused"
    assert (project / "prompts/C01_face.txt").read_text(encoding="utf-8") == "Portrait of Mara, face plate"


def test_quota_stops_the_run_with_exit_3_and_keeps_progress(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_image.run(project, config=_command_config(tmp_path, "LOC01", "quota"), sleep=lambda s: None)
    assert code == 3
    assert summary["errors"] == ["quota: refused"]
    story = load_story(project)
    assert story["cast"][1]["plates"]["full"]["status"] == "done"
    assert story["slides"][0]["image"]["status"] == "pending"


def test_wrong_aspect_marks_needs_human(tmp_path):
    project = write_project(tmp_path, make_story())
    config = _command_config(tmp_path, "never", "invalid")
    script = tmp_path / "provider.py"
    script.write_text(script.read_text().replace('"9:16": (36, 64)', '"9:16": (64, 64)'), encoding="utf-8")
    summary, code = sf_image.run(project, config=config)
    assert code == 2
    assert "LOC01" in summary["needs_human"]
    assert "expected aspect 9:16" in load_story(project)["locations"][0]["plate"]["last_error"]
    assert load_story(project)["locations"][0]["plate"]["attempts"] == 3
    assert summary["blocked"] == ["S01 waits for LOC01", "S02 waits for LOC01"]


def test_quality_failure_is_regenerated_then_passes(tmp_path):
    script = tmp_path / "provider.py"
    script.write_text(textwrap.dedent("""
        import json, sys, os
        from pathlib import Path
        from PIL import Image
        args = sys.argv[1:]
        out = args[args.index("--out") + 1]
        aspect = args[args.index("--aspect") + 1]
        sizes = {"1:1": (64, 64), "3:4": (48, 64), "9:16": (36, 64), "16:9": (64, 36)}
        # Track calls: first call writes wrong size, second call writes correct size
        counter_file = Path(out).parent / ".call_count"
        call_num = int(counter_file.read_text()) if counter_file.exists() else 0
        counter_file.write_text(str(call_num + 1))
        if call_num == 0:
            Image.new("RGB", (50, 64), "gray").save(out)
        else:
            Image.new("RGB", sizes[aspect], "gray").save(out)
    """), encoding="utf-8")
    config = {"image": {"provider": "command", "command": [sys.executable, str(script)], "timeout_s": 30, "max_refs": 4}}
    project = write_project(tmp_path, make_story())
    summary, code = sf_image.run(project, config=config)
    assert code == 0
    assert summary["done"] == ["C01_face", "C01_half", "C01_full", "LOC01", "S01", "S02"]
    assert load_story(project)["cast"][1]["plates"]["face"]["attempts"] == 2
