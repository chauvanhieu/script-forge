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


def _split_lines(cue: list[dict], max_chars: int, spaced: bool) -> list[list[dict]]:
    if _joined_len(cue, spaced) <= max_chars or len(cue) == 1:
        return [cue]
    best = min(range(1, len(cue)), key=lambda k: abs(_joined_len(cue[:k], spaced) - _joined_len(cue[k:], spaced)))
    return [cue[:best], cue[best:]]


def _fits(cue: list[dict], max_chars: int, spaced: bool) -> bool:
    """Whether cue renders (as a single row, or the best 2-way split) with every row <= max_chars."""
    return all(_joined_len(row, spaced) <= max_chars for row in _split_lines(cue, max_chars, spaced))


def _chunk(words: list[dict], max_chars: int, max_lines: int, spaced: bool) -> list[list[dict]]:
    limit = max_chars * max_lines
    cues, current = [], []
    for word in words:
        if current and not _fits(current + [word], max_chars, spaced):
            cues.append(current)
            current = []
        current.append(word)
        if word["text"].endswith(SENTENCE_END) and _joined_len(current, spaced) >= limit / 2:
            cues.append(current)
            current = []
    if current:
        cues.append(current)
    return cues


def _active_word_text(rows: list[list[dict]], active_word_id: int, caption_color: str, unsung_color: str, spaced: bool) -> str:
    joiner = " " if spaced else ""
    rendered = []
    base_color_tag = f"\\c{ass_color(unsung_color)}"
    for row in rows:
        row_text = []
        for w in row:
            text = _escape(w["text"])
            if id(w) == active_word_id:
                # Subtle flash: starts bright white, fades to caption_color over 60ms for a punchy visual hit
                flash_tag = f"{{\\c&HFFFFFF&\\t(0,60,\\c{ass_color(caption_color)})}}"
                row_text.append(f"{flash_tag}{text}{{\\c{ass_color(unsung_color)}}}")
            else:
                row_text.append(text)
        rendered.append(joiner.join(row_text))
    return f"{{{base_color_tag}}}" + "\\N".join(rendered)


def _cue_text(rows: list[list[dict]], spaced: bool) -> str:
    joiner = " " if spaced else ""
    rendered = []
    for row in rows:
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
    animation = story["brief"]["captions"].get("animation", "none")
    if mode == "none":
        story["output"]["captions"] = None
        save_story(project_dir, story)
        return {"mode": mode, "cues": 0, "needs_human": []}, EXIT_OK
    stale = [f"{line['id']}: words are missing or stale; run sf_align" for line in story["lines"]
             if line.get("words_hash") is None or line["words_hash"] != line["audio"].get("input_hash")]
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
    last_event_end = 0
    for line in story["lines"]:
        start = timeline.line_start_ms[line["id"]]
        line_end = timeline.line_end_ms[line["id"]]
        where = placement[line["id"]]
        margin_v = round(style["margin_v_pct"][aspect][where] * height)
        chunks = [[w] for w in line["words"]] if animation == "word_by_word" else _chunk(line["words"], max_chars, style["max_lines"], spaced)
        for cue in chunks:
            rows = _split_lines(cue, max_chars, spaced)
            cue_start = max(start, start + cue[0]["start_ms"])
            cue_end = min(line_end, max(start + cue[-1]["end_ms"], cue_start + 10))
            if animation == "word_by_word":
                cue_start = max(start, cue_start - 40)
                cue_end = min(line_end, max(cue_start + 10, cue_end - 40))
            
            is_karaoke = (mode == "karaoke") and (animation != "word_by_word")
            if is_karaoke:
                speaker_id = line["speaker"]
                speaker_color = next((m["caption_color"] for m in story["cast"] if m["id"] == speaker_id), "#FFFF00")
                unsung_color = style.get("unsung_color", "#FFFFFF")
                flat = [w for row in rows for w in row]
                
                PRE_ROLL = 40
                
                for index, word in enumerate(flat):
                    w_start_orig = start + word["start_ms"]
                    w_end_orig = start + word["end_ms"]
                    
                    w_start = max(start, max(last_event_end, w_start_orig - PRE_ROLL))
                    
                    next_start_orig = start + flat[index + 1]["start_ms"] if index + 1 < len(flat) else None
                    
                    # Determine active event duration and gap handling
                    if next_start_orig is not None:
                        next_start = max(start, next_start_orig - PRE_ROLL)
                        gap = next_start_orig - w_end_orig
                        if gap > 80:  # Perceptual gap threshold
                            w_end = min(line_end, max(w_start + 10, w_end_orig))
                            has_gap = True
                        else:
                            w_end = min(line_end, max(w_start + 10, next_start))
                            has_gap = False
                    else:
                        w_end = min(line_end, max(w_end_orig, w_start + 10))
                        has_gap = False
                        next_start = None
                        
                    # Create the active word event
                    text_content = _active_word_text(rows, id(word), speaker_color, unsung_color, spaced)
                    text = f"{{\\an{ALIGNMENT[where]}}}" + text_content
                    events.append(f"Dialogue: 0,{ass_time(w_start)},{ass_time(w_end)},{line['speaker']},{line['id']},0,0,{margin_v},,{text}")
                    last_event_end = w_end
                    
                    # Create the REST event if there's a significant gap
                    if has_gap and next_start is not None and next_start > w_end:
                        rest_start = w_end
                        rest_end = min(line_end, max(rest_start + 10, next_start))
                        rest_content = _active_word_text(rows, -1, speaker_color, unsung_color, spaced)
                        rest_text = f"{{\\an{ALIGNMENT[where]}}}" + rest_content
                        events.append(f"Dialogue: 0,{ass_time(rest_start)},{ass_time(rest_end)},{line['speaker']},{line['id']},0,0,{margin_v},,{rest_text}")
                        last_event_end = rest_end
                continue

            cue_start = max(start, max(last_event_end, cue_start))
            cue_end = min(line_end, max(cue_start + 10, cue_end))
            last_event_end = cue_end
            base_text = _cue_text(rows, spaced)
            cue_dur = cue_end - cue_start
            anim_tags = ""
            
            if animation == "pop_up":
                in_dur = min(100, max(10, cue_dur // 2))
                back_dur = min(60, max(10, cue_dur // 3))
                anim_tags = f"{{\\fscx0\\fscy0\\t(0,{in_dur},1.5,\\fscx110\\fscy110)\\t({in_dur},{in_dur+back_dur},1,\\fscx100\\fscy100)}}"
            elif animation == "slide_blur":
                slide_dur = min(800, cue_dur)
                out_dur = min(200, cue_dur // 3)
                out_start = cue_dur - out_dur
                
                x = SIZE[aspect][0] // 2
                y = margin_v if where == "upper_third" else (height // 2 if where == "center" else height - margin_v)
                
                anim_tags = f"{{\\move({x},{y+60},{x},{y},0,{slide_dur})\\fad(150,0)\\t({out_start},{cue_dur},\\blur5\\alpha&HFF&)}}"
                
            text = f"{{\\an{ALIGNMENT[where]}}}" + anim_tags + base_text
            events.append(f"Dialogue: 0,{ass_time(cue_start)},{ass_time(cue_end)},{line['speaker']},{line['id']},0,0,{margin_v},,{text}")
    out = project_dir / "out" / "captions.ass"
    out.parent.mkdir(exist_ok=True)
    out.write_text(_header(story, style) + "\n" + "\n".join(events) + "\n", encoding="utf-8")
    story["output"]["captions"] = "out/captions.ass"
    save_story(project_dir, story)
    return {"mode": mode, "cues": len(events), "needs_human": []}, EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
