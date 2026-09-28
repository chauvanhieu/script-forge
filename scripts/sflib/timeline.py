"""Absolute timeline built from measured line durations."""
from __future__ import annotations

from dataclasses import dataclass

FPS = 30


def ms_to_frame(ms: int) -> int:
    return round(ms * FPS / 1000)


@dataclass(frozen=True)
class SlideSpan:
    slide_id: str
    start_ms: int
    end_ms: int
    start_frame: int
    end_frame: int

    @property
    def frames(self) -> int:
        return self.end_frame - self.start_frame


@dataclass(frozen=True)
class Timeline:
    line_start_ms: dict[str, int]
    line_end_ms: dict[str, int]
    slides: list[SlideSpan]
    total_ms: int

    @property
    def total_frames(self) -> int:
        return ms_to_frame(self.total_ms)


def build_timeline(story: dict) -> Timeline:
    """Lines play back to back with their pauses; a slide spans from its first line to the next slide."""
    starts: dict[str, int] = {}
    ends: dict[str, int] = {}
    cursor = 0
    for line in story["lines"]:
        duration = (line.get("audio") or {}).get("duration_ms")
        if not duration:
            raise ValueError(f"line {line['id']} has no measured duration; run sf_voice first")
        starts[line["id"]] = cursor
        ends[line["id"]] = cursor + duration
        cursor += duration + line.get("pause_after_ms", 0)
    slide_starts = [starts[slide["line_ids"][0]] for slide in story["slides"]]
    spans = []
    for index, slide in enumerate(story["slides"]):
        start = slide_starts[index]
        end = slide_starts[index + 1] if index + 1 < len(slide_starts) else cursor
        spans.append(SlideSpan(slide["id"], start, end, ms_to_frame(start), ms_to_frame(end)))
    return Timeline(starts, ends, spans, cursor)
