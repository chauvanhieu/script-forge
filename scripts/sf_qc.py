#!/usr/bin/env python3
"""Measure the rendered video against the timeline and write out/qc.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

from sf_captions import SIZE, STYLES_DIR, load_style
from sflib.media import probe_audio_ms, probe_video, silences
from sflib.project import EXIT_HUMAN, EXIT_OK, load_story, main_wrapper, save_story
from sflib.timeline import FPS, build_timeline

AUDIO_TOLERANCE_MS = 60 + round(1000 / FPS)
OVERLAP_TOLERANCE_MS = 10
SILENCE_GRACE_S = 0.3
_DIALOGUE = re.compile(r"^Dialogue: \d+,([^,]+),([^,]+),[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,(.*)$")


def _ms(ass_time: str) -> int:
    hours, minutes, rest = ass_time.split(":")
    seconds, centis = rest.split(".")
    return ((int(hours) * 60 + int(minutes)) * 60 + int(seconds)) * 1000 + int(centis) * 10


def _check(name: str, ok: bool, detail: str) -> dict:
    return {"name": name, "ok": bool(ok), "detail": detail}


def _caption_checks(story: dict, project_dir: Path, total_ms: int, styles_dir: Path) -> list[dict]:
    captions = story["output"].get("captions")
    if story["brief"]["captions"]["mode"] == "none" or not captions:
        return [_check("caption_timing", True, "no captions"), _check("caption_line_length", True, "no captions")]
    events = []
    for raw in (project_dir / captions).read_text(encoding="utf-8").splitlines():
        match = _DIALOGUE.match(raw)
        if match:
            events.append((_ms(match.group(1)), _ms(match.group(2)), match.group(3)))
    events.sort()
    timing_problems = [f"cue at {s} ms ends at {e} ms" for s, e, _ in events if e <= s or e > total_ms + OVERLAP_TOLERANCE_MS]
    timing_problems += [f"cue at {events[i + 1][0]} ms overlaps the cue ending at {events[i][1]} ms"
                        for i in range(len(events) - 1) if events[i + 1][0] < events[i][1] - OVERLAP_TOLERANCE_MS]
    style = load_style(story["brief"]["captions"]["style"], styles_dir)
    max_chars = style["max_chars_per_line"][story["brief"]["aspect"]]
    long_rows = [row for _, _, text in events for row in re.sub(r"\{[^}]*\}", "", text).split("\\N") if len(row) > max_chars]
    return [
        _check("caption_timing", not timing_problems, "; ".join(timing_problems) or f"{len(events)} cues ok"),
        _check("caption_line_length", not long_rows, f"rows over {max_chars} chars: {long_rows}" if long_rows else "ok"),
    ]


def run(project_dir: Path, only: set[str] | None = None, size: tuple[int, int] | None = None,
        styles_dir: Path = STYLES_DIR) -> tuple[dict, int]:
    story = load_story(project_dir)
    not_done = [line["id"] for line in story["lines"] if line["audio"].get("status") != "done"]
    not_done += [slide["id"] for slide in story["slides"] if slide["image"].get("status") != "done"]
    checks = [_check("assets_done", not not_done, f"not done: {not_done}" if not_done else "ok")]
    video_path = project_dir / (story["output"].get("video") or "out/final.mp4")
    try:
        timeline = build_timeline(story)
    except ValueError as exc:
        reason = f"timeline unavailable: {exc}"
        checks += [_check(name, False, reason) for name in
                  ("frames_match", "audio_duration", "resolution", "caption_timing", "caption_line_length", "silence")]
        timeline = None
    if timeline is not None:
        if video_path.is_file():
            video = probe_video(video_path)
            audio_ms = probe_audio_ms(video_path)
            expected_size = size or SIZE[story["brief"]["aspect"]]
            checks.append(_check("frames_match", abs(video["frames"] - timeline.total_frames) <= 1,
                                 f"video {video['frames']} frames, timeline {timeline.total_frames}"))
            checks.append(_check("audio_duration", abs(audio_ms - timeline.total_ms) <= AUDIO_TOLERANCE_MS,
                                 f"audio {audio_ms} ms, timeline {timeline.total_ms} ms"))
            checks.append(_check("resolution", (video["width"], video["height"]) == tuple(expected_size),
                                 f"{video['width']}x{video['height']}, expected {expected_size[0]}x{expected_size[1]}"))
        else:
            checks += [_check(name, False, f"{video_path.name} not rendered") for name in ("frames_match", "audio_duration", "resolution")]
        checks += _caption_checks(story, project_dir, timeline.total_ms, styles_dir)
        if video_path.is_file():
            allowed = max(line.get("pause_after_ms", 0) for line in story["lines"]) / 1000 + SILENCE_GRACE_S
            long_gaps = [round(gap, 2) for gap in silences(video_path) if gap > allowed]
            checks.append(_check("silence", not long_gaps, f"silences over {allowed:.2f}s: {long_gaps}" if long_gaps else "ok"))
        else:
            checks.append(_check("silence", False, "not rendered"))
    words = [word for line in story["lines"] for word in line.get("words") or []]
    approx_ratio = round(sum(word["approx"] for word in words) / len(words), 3) if words else 0.0
    report = {"checks": checks, "approx_ratio": approx_ratio}
    out = project_dir / "out" / "qc.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    story["output"]["qc"] = "out/qc.json"
    save_story(project_dir, story)
    failed = [check["name"] for check in checks if not check["ok"]]
    return {"failed": failed, "approx_ratio": approx_ratio}, EXIT_HUMAN if failed else EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
