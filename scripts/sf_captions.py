#!/usr/bin/env python3
"""Build out/captions.ass (karaoke or plain) from aligned words and the timeline."""
from __future__ import annotations

from pathlib import Path

import yaml

from sflib.project import EXIT_HUMAN, EXIT_OK, ROOT, load_story, main_wrapper, save_story
from sflib.text import uses_clusters
from sflib.timeline import build_timeline

STYLES_DIR = ROOT / "config" / "caption-styles"
SIZE = {"9:16": (1080, 1920), "16:9": (1920, 1080)}
ALIGNMENT = {"lower_third": 2, "center": 5, "upper_third": 8}
SENTENCE_END = (".", "!", "?", "…", "。", "！", "？")
MARGIN_LR = 60


def ass_color(hex_rgb: str) -> str:
    red, green, blue = hex_rgb[1:3], hex_rgb[3:5], hex_rgb[5:7]
    return f"&H00{blue}{green}{red}".upper()


def ass_time(ms: int) -> str:
    cs = round(ms / 10)
    return f"{cs // 360000}:{(cs // 6000) % 60:02d}:{(cs // 100) % 60:02d}.{cs % 100:02d}"


def load_style(name: str, styles_dir: Path = STYLES_DIR) -> dict:
    return yaml.safe_load((styles_dir / f"{name}.yaml").read_text(encoding="utf-8"))


def _escape(text: str) -> str:
    return text.replace("\\", "/").replace("{", "(").replace("}", ")")


def _joined_len(words: list[dict], spaced: bool) -> int:
    return sum(len(w["text"]) for w in words) + (len(words) - 1 if spaced else 0)


def _chunk(words: list[dict], limit: int, spaced: bool) -> list[list[dict]]:
    cues, current = [], []
    for word in words:
        if current and _joined_len(current + [word], spaced) > limit:
            cues.append(current)
            current = []
        current.append(word)
        if word["text"].endswith(SENTENCE_END) and _joined_len(current, spaced) >= limit / 2:
            cues.append(current)
            current = []
    if current:
        cues.append(current)
    return cues


def _split_lines(cue: list[dict], max_chars: int, spaced: bool) -> list[list[dict]]:
    if _joined_len(cue, spaced) <= max_chars or len(cue) == 1:
        return [cue]
    best = min(range(1, len(cue)), key=lambda k: abs(_joined_len(cue[:k], spaced) - _joined_len(cue[k:], spaced)))
    return [cue[:best], cue[best:]]


def _cue_text(rows: list[list[dict]], karaoke: bool, spaced: bool) -> str:
    flat = [word for row in rows for word in row]
    durations = {}
    for index, word in enumerate(flat):
        until = flat[index + 1]["start_ms"] if index + 1 < len(flat) else word["end_ms"]
        durations[id(word)] = max(0, round((until - word["start_ms"]) / 10))
    joiner = " " if spaced else ""
    rendered = []
    for row in rows:
        if karaoke:
            rendered.append(joiner.join(f"{{\\kf{durations[id(w)]}}}{_escape(w['text'])}" for w in row))
        else:
            rendered.append(joiner.join(_escape(w["text"]) for w in row))
    return "\\N".join(rendered)


def _header(story: dict, style: dict) -> str:
    aspect = story["brief"]["aspect"]
    width, height = SIZE[aspect]
    bold = -1 if style["bold"] else 0
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {width}", f"PlayResY: {height}",
        "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
    ]
    for member in story["cast"]:
        lines.append(
            f"Style: {member['id']},{style['font']},{style['font_size'][aspect]},{ass_color(member['caption_color'])},"
            f"{ass_color(style['unsung_color'])},&H00000000,&H80000000,{bold},0,0,0,100,100,0,0,1,"
            f"{style['outline']},{style['shadow']},2,{MARGIN_LR},{MARGIN_LR},0,1"
        )
    lines += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    return "\n".join(lines)


def run(project_dir: Path, only: set[str] | None = None, styles_dir: Path = STYLES_DIR) -> tuple[dict, int]:
    story = load_story(project_dir)
    mode = story["brief"]["captions"]["mode"]
    if mode == "none":
        story["output"]["captions"] = None
        save_story(project_dir, story)
        return {"mode": mode, "cues": 0, "needs_human": []}, EXIT_OK
    stale = [f"{line['id']}: words are missing or stale; run sf_align" for line in story["lines"]
             if not line.get("words") or line.get("words_hash") != line["audio"].get("input_hash")]
    if stale:
        return {"mode": mode, "cues": 0, "needs_human": stale}, EXIT_HUMAN
    style = load_style(story["brief"]["captions"]["style"], styles_dir)
    aspect = story["brief"]["aspect"]
    height = SIZE[aspect][1]
    spaced = not uses_clusters(story["brief"]["language"])
    max_chars = style["max_chars_per_line"][aspect]
    timeline = build_timeline(story)
    placement = {lid: slide["visual"]["text_placement"] for slide in story["slides"] for lid in slide["line_ids"]}
    events = []
    for line in story["lines"]:
        start = timeline.line_start_ms[line["id"]]
        where = placement[line["id"]]
        margin_v = round(style["margin_v_pct"][aspect][where] * height)
        for cue in _chunk(line["words"], max_chars * style["max_lines"], spaced):
            rows = _split_lines(cue, max_chars, spaced)
            cue_start = start + cue[0]["start_ms"]
            cue_end = max(start + cue[-1]["end_ms"], cue_start + 10)
            text = f"{{\\an{ALIGNMENT[where]}}}" + _cue_text(rows, mode == "karaoke", spaced)
            events.append(f"Dialogue: 0,{ass_time(cue_start)},{ass_time(cue_end)},{line['speaker']},,0,0,{margin_v},,{text}")
    out = project_dir / "out" / "captions.ass"
    out.parent.mkdir(exist_ok=True)
    out.write_text(_header(story, style) + "\n" + "\n".join(events) + "\n", encoding="utf-8")
    story["output"]["captions"] = "out/captions.ass"
    save_story(project_dir, story)
    return {"mode": mode, "cues": len(events), "needs_human": []}, EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
