import json
from pathlib import Path
from PIL import Image

import sf_init
import sf_sync_gemini_images


def test_sync_gemini_images(tmp_path):
    # 1. Setup mock brain dir
    brain_dir = tmp_path / "mock_brain"
    brain_dir.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (512, 512), color="red")
    img_path = brain_dir / "my-video_s01_17900000.jpg"
    img.save(img_path, format="JPEG")

    # 2. Setup project
    project_dir = tmp_path / "projects" / "my-video"
    sf_init.init_project(project_dir)

    # 3. Run sync
    summary, code = sf_sync_gemini_images.sync_images(project_dir, brain_dir=brain_dir)
    assert code == 0
    assert summary["ok"] is True
    assert "S01" in summary["synced"]

    # 4. Check image in project
    target_png = project_dir / "images" / "S01.png"
    assert target_png.exists()
    with Image.open(target_png) as out_img:
        assert out_img.size == (1080, 1920)
        assert out_img.format == "PNG"

    # 5. Check story.json updated
    story = json.loads((project_dir / "story.json").read_text(encoding="utf-8"))
    s01 = story["slides"][0]
    assert s01["image"]["status"] == "done"
    assert s01["image"]["path"] == "images/S01.png"
    assert s01["image"]["input_hash"] is not None


def test_sync_character_and_location_plates(tmp_path):
    brain_dir = tmp_path / "mock_brain"
    brain_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create mock plate files in brain
    face_img = Image.new("RGB", (512, 512), color="blue")
    face_img.save(brain_dir / "story-slug_c01_face_8899.png")

    loc_img = Image.new("RGB", (720, 1280), color="green")
    loc_img.save(brain_dir / "story-slug_loc01_master_7766.png")

    # 2. Init project and configure C01 with plates and LOC01
    project_dir = tmp_path / "projects" / "story-slug"
    sf_init.init_project(project_dir)

    story_path = project_dir / "story.json"
    story = json.loads(story_path.read_text(encoding="utf-8"))
    story["cast"].append({
        "id": "C01",
        "canon_id": None,
        "name": "Hero",
        "role": "protagonist",
        "caption_color": "#FFCC00",
        "voice": {"source": "design", "design_prompt": "heroic male", "profile_id": None},
        "plates": {
            "face": {"path": None, "input_hash": None, "status": "pending", "attempts": 0, "last_error": None, "prompt": "face portrait"},
            "half": {"path": None, "input_hash": None, "status": "pending", "attempts": 0, "last_error": None, "prompt": "half body"},
            "full": {"path": None, "input_hash": None, "status": "pending", "attempts": 0, "last_error": None, "prompt": "full body"}
        }
    })
    story_path.write_text(json.dumps(story), encoding="utf-8")

    # 3. Sync plates
    summary, code = sf_sync_gemini_images.sync_images(project_dir, brain_dir=brain_dir)
    assert "C01_face" in summary["synced"]
    assert "LOC01" in summary["synced"]

    # 4. Check plates on disk
    assert (project_dir / "plates" / "C01_face.png").exists()
    assert (project_dir / "plates" / "LOC01.png").exists()

    # 5. Check story.json updated
    updated_story = json.loads(story_path.read_text(encoding="utf-8"))
    c01_face = updated_story["cast"][1]["plates"]["face"]
    assert c01_face["status"] == "done"
    assert c01_face["path"] == "plates/C01_face.png"
    assert c01_face["input_hash"] is not None

    loc01_plate = updated_story["locations"][0]["plate"]
    assert loc01_plate["status"] == "done"
    assert loc01_plate["path"] == "plates/LOC01.png"

