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
