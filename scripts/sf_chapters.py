#!/usr/bin/env python3
"""Assemble a long-form story.json from chapters/ch*.json plus chapters/episode.json (long-form sleep profile).

chapters/chNN.json: {"chapter", "title", "slides": [{"moment", "prompt", "shot", "motion", "lines": [...]}]}
chapters/episode.json: {"brief": {...overrides}, "style_bible", "cast", "research", "seo", "style_suffix",
                        "pause_ms": {"line", "chapter_end", "final"}}
Writes story.json lines/slides (all assets pending), script.md, and chapters/index.json (chapter -> first line id).
"""
from __future__ import annotations

import json
import re
import zlib
from pathlib import Path

from sflib.project import EXIT_HUMAN, EXIT_OK, load_story, main_wrapper, save_story

BANNED = re.compile(r"[0-9\"“”()\[\];—…]")  # TTS rules: digits, quotes, brackets, semicolons, em dashes, ellipses


def build(story: dict, episode: dict, chapters: list[dict]) -> tuple[dict, list[dict], list[str]]:
    pauses = {"line": 800, "chapter_end": 2000, "final": 3000, **episode.get("pause_ms", {})}
    suffix = episode.get("style_suffix", "")
    lines, slides, index, problems = [], [], [], []
    for c_i, chapter in enumerate(chapters):
        index.append({"chapter": chapter["chapter"], "title": chapter["title"], "first_line": f"L{len(lines) + 1:03d}"})
        for slide in chapter["slides"]:
            line_ids = []
            for text in slide["lines"]:
                text = " ".join(text.split())
                lid = f"L{len(lines) + 1:03d}"
                if BANNED.search(text):
                    problems.append(f"{lid}: banned character in {text[:60]!r}")
                lines.append({
                    "id": lid, "speaker": "narrator", "text": text, "whisper": False, "pause_after_ms": pauses["line"],
                    "claim_ids": [], "words": [], "words_hash": None,
                    "audio": {"path": f"audio/{lid}.wav", "input_hash": None, "status": "pending", "attempts": 0,
                              "last_error": None, "duration_ms": None, "seed": None, "qc": None, "asr_words": None},
                })
                line_ids.append(lid)
            sid = f"S{len(slides) + 1:03d}"
            prompt = f"{slide['prompt'].rstrip(' .,')}, {suffix}" if suffix else slide["prompt"]
            slides.append({
                "id": sid, "source": None, "line_ids": line_ids,
                "brief": {"moment": slide["moment"], "characters": [], "location": None, "must_show": [],
                          "must_not_show": ["text", "modern objects"], "continuity": [], "beat": "setup"},
                "visual": {"prompt": prompt, "shot": slide["shot"], "motion": slide["motion"], "text_placement": "center"},
                "image": {"path": f"images/{sid}.png", "input_hash": None, "status": "pending", "attempts": 0,
                          "last_error": None, "seed": zlib.crc32(f"{story['slug']}:{sid}".encode()) % 2_147_483_647},
            })
        lines[-1]["pause_after_ms"] = pauses["final"] if c_i == len(chapters) - 1 else pauses["chapter_end"]
    for key in ("style_bible", "cast", "research", "seo"):
        if key in episode:
            story[key] = episode[key]
    story["brief"].update(episode.get("brief", {}))
    story["locations"], story["lines"], story["slides"] = [], lines, slides
    return story, index, problems


def script_md(story: dict, chapters: list[dict]) -> str:
    out = [f"# {story.get('seo', {}).get('title', story['slug'])}\n"]
    for chapter in chapters:
        out.append(f"\n## {chapter['chapter']}. {chapter['title']}\n")
        out += [" ".join(slide["lines"]) + "\n" for slide in chapter["slides"]]
    return "\n".join(out)


def run(project_dir: Path, only: set[str] | None = None) -> tuple[dict, int]:
    chapter_dir = project_dir / "chapters"
    chapters = [json.loads(p.read_text()) for p in sorted(chapter_dir.glob("ch*.json"))]
    if not chapters:
        return {"needs_human": ["no chapters/ch*.json"]}, EXIT_HUMAN
    episode = json.loads((chapter_dir / "episode.json").read_text())
    story, index, problems = build(load_story(project_dir), episode, chapters)
    save_story(project_dir, story)
    (project_dir / "script.md").write_text(script_md(story, chapters))
    (chapter_dir / "index.json").write_text(json.dumps(index, indent=2))
    words = sum(len(line["text"].split()) for line in story["lines"])
    summary = {"chapters": len(chapters), "slides": len(story["slides"]), "lines": len(story["lines"]),
               "words": words, "needs_human": problems}
    return summary, EXIT_HUMAN if problems else EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
