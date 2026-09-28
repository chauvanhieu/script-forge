#!/usr/bin/env python3
"""Build out/contact_sheet.png: every plate and slide with its id, for Gate 2 review."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from sflib.project import EXIT_HUMAN, EXIT_OK, load_story, main_wrapper, save_story
from sflib.text import display_text

CELL = {"9:16": (270, 480), "16:9": (480, 270)}
COLS = {"9:16": 6, "16:9": 4}
LABEL_H = 56
PAD = 12


def _tiles(story: dict) -> list[tuple[str, str, str | None]]:
    """(id, caption, image path or None) for plates, then slides."""
    tiles = []
    for member in story["cast"]:
        for kind, plate in (member.get("plates") or {}).items():
            tiles.append((f"{member['id']}_{kind}", member["name"], plate["path"] if plate["status"] == "done" else None))
    for location in story["locations"]:
        plate = location["plate"]
        tiles.append((location["id"], location["name"], plate["path"] if plate["status"] == "done" else None))
    lines = {line["id"]: line for line in story["lines"]}
    for slide in story["slides"]:
        first = display_text(lines[slide["line_ids"][0]]["text"])
        image = slide["image"]
        tiles.append((slide["id"], first[:40], image["path"] if image["status"] == "done" else None))
    return tiles


def run(project_dir: Path, only: set[str] | None = None) -> tuple[dict, int]:
    story = load_story(project_dir)
    aspect = story["brief"]["aspect"]
    cell_w, cell_h = CELL[aspect]
    tiles = _tiles(story)
    cols = min(COLS[aspect], len(tiles))
    rows = math.ceil(len(tiles) / cols)
    sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * PAD, rows * (cell_h + LABEL_H) + (rows + 1) * PAD), "#1e1e1e")
    draw = ImageDraw.Draw(sheet)
    id_font = ImageFont.load_default(size=20)
    caption_font = ImageFont.load_default(size=14)
    missing = []
    for index, (item, caption, rel_path) in enumerate(tiles):
        x = PAD + (index % cols) * (cell_w + PAD)
        y = PAD + (index // cols) * (cell_h + LABEL_H + PAD)
        path = project_dir / rel_path if rel_path else None
        if path and path.exists():
            with Image.open(path) as image:
                thumb = ImageOps.contain(image.convert("RGB"), (cell_w, cell_h))
            sheet.paste(thumb, (x + (cell_w - thumb.width) // 2, y + (cell_h - thumb.height) // 2))
        else:
            missing.append(item)
            draw.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], fill="#555555")
            draw.text((x + cell_w // 2, y + cell_h // 2), "MISSING", fill="white", anchor="mm", font=id_font)
        draw.text((x, y + cell_h + 6), item, fill="white", font=id_font)
        draw.text((x, y + cell_h + 32), caption, fill="#bbbbbb", font=caption_font)
    out = project_dir / "out" / "contact_sheet.png"
    out.parent.mkdir(exist_ok=True)
    sheet.save(out)
    story["output"]["contact_sheet"] = "out/contact_sheet.png"
    save_story(project_dir, story)
    return {"tiles": len(tiles), "missing": missing}, EXIT_HUMAN if missing else EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
