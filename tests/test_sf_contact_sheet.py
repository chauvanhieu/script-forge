from pathlib import Path

import pytest
from PIL import Image

from fixtures import make_story, write_project
import sf_contact_sheet
import sf_image
from sflib.project import load_story


def test_contact_sheet_has_every_plate_and_slide(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_image.run(project, config={"image": {"provider": "fake", "max_refs": 4}})
    summary, code = sf_contact_sheet.run(project)
    assert code == 0
    assert summary == {"tiles": 6, "missing": []}
    sheet = Image.open(project / "out/contact_sheet.png")
    # 6 tiles in one row of 6 columns: width = 6*270 + 7*12, height = 480 + 56 + 2*12
    assert sheet.size == (6 * 270 + 7 * 12, 480 + 56 + 2 * 12)
    assert load_story(project)["output"]["contact_sheet"] == "out/contact_sheet.png"


def test_missing_images_are_reported(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_contact_sheet.run(project)
    assert code == 2
    assert summary["missing"] == ["C01_face", "C01_half", "C01_full", "LOC01", "S01", "S02"]


def test_font_uses_a_system_truetype_font_when_one_exists():
    available = [p for p in sf_contact_sheet._FONT_PATHS if Path(p).exists()]
    if not available:
        pytest.skip("no system TrueType font with Vietnamese coverage on this machine")
    font = sf_contact_sheet._font(20)
    # a real font file (Vietnamese glyphs like "ố" render correctly), not PIL's load_default fallback
    assert font.path in available


def test_font_skips_a_corrupt_font_file_and_falls_back_to_default(tmp_path, monkeypatch):
    bad = tmp_path / "corrupt.ttf"
    bad.write_bytes(b"not a font")  # exists, but PIL raises OSError trying to load it
    monkeypatch.setattr(sf_contact_sheet, "_FONT_PATHS", (str(bad),))
    font = sf_contact_sheet._font(20)  # must not raise
    assert not isinstance(getattr(font, "path", None), str)  # fell through to load_default


def test_font_skips_a_corrupt_font_file_and_falls_through_to_a_good_one(tmp_path, monkeypatch):
    bad = tmp_path / "corrupt.ttf"
    bad.write_bytes(b"not a font")
    good = [p for p in sf_contact_sheet._FONT_PATHS if Path(p).exists()]
    if not good:
        pytest.skip("no system TrueType font available on this machine")
    monkeypatch.setattr(sf_contact_sheet, "_FONT_PATHS", (str(bad), good[0]))
    font = sf_contact_sheet._font(20)
    assert font.path == good[0]
