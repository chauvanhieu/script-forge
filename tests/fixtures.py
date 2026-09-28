"""Builders for test productions."""
from __future__ import annotations

import copy
import io
import json
import math
import struct
import wave
from pathlib import Path


def asset(**extra) -> dict:
    return {"path": None, "input_hash": None, "status": "pending", "attempts": 0, "last_error": None, **extra}


def _line(line_id: str, speaker: str, text: str, pause: int, whisper: bool = False) -> dict:
    return {
        "id": line_id,
        "speaker": speaker,
        "text": text,
        "whisper": whisper,
        "pause_after_ms": pause,
        "claim_ids": [],
        "audio": asset(duration_ms=None, seed=None, qc=None, asr_words=None),
        "words": [],
        "words_hash": None,
    }


BASE = {
    "schema_version": "1.0",
    "slug": "demo-ch01-916-en",
    "canon": {"path": "stories/demo", "chapters": ["chapter-01"]},
    "brief": {
        "idea": "A lighthouse keeper sees a second light.",
        "language": "en",
        "aspect": "9:16",
        "content_type": "fiction",
        "genre": "mystery",
        "target_seconds": 30,
        "captions": {"mode": "karaoke", "style": "karaoke-bold"},
        "review_mode": "gated",
    },
    "state": {"stage": "adapt", "gates": {"script": {"approved_at": None}, "images": {"approved_at": None}}},
    "style_bible": {
        "medium": "painterly digital illustration",
        "palette": ["navy", "amber"],
        "lighting": "low moonlight",
        "composition": "one clear subject",
        "avoid": ["generated text", "logos", "watermarks"],
    },
    "cast": [
        {
            "id": "narrator",
            "canon_id": None,
            "name": "Narrator",
            "role": "narrator",
            "voice": {"source": "design", "design_prompt": "male, middle-aged, low pitch", "profile_id": None},
            "caption_color": "#FFFFFF",
        },
        {
            "id": "C01",
            "canon_id": "mara-quill",
            "name": "Mara",
            "role": "protagonist",
            "appearance": "woman in her 40s, grey oilskin coat, short dark hair",
            "voice": {"source": "design", "design_prompt": "female, middle-aged, moderate pitch", "profile_id": None},
            "caption_color": "#FFD166",
            "plates": {
                "face": asset(prompt="Portrait of Mara, face plate"),
                "half": asset(prompt="Mara, half-body plate"),
                "full": asset(prompt="Mara, full-body plate"),
            },
        },
    ],
    "locations": [
        {
            "id": "LOC01",
            "canon_id": "skerry-light",
            "name": "Skerry Light",
            "appearance": "stone lighthouse on a black rock",
            "plate": asset(prompt="Skerry Light lighthouse at night, location plate"),
        }
    ],
    "slides": [
        {
            "id": "S01",
            "source": "chapter-01-scene-01",
            "line_ids": ["L001", "L002"],
            "brief": {
                "moment": "Mara climbs the harbor wall",
                "characters": ["C01"],
                "location": "LOC01",
                "must_show": [],
                "must_not_show": ["the second light"],
                "continuity": ["grey oilskin coat"],
                "beat": "setup",
            },
            "visual": {"prompt": "Mara climbs the harbor wall at night", "shot": "wide", "motion": "push_in", "text_placement": "lower_third"},
            "image": asset(seed=11),
        },
        {
            "id": "S02",
            "source": "chapter-01-scene-01",
            "line_ids": ["L003"],
            "brief": {
                "moment": "A second light glows on the water",
                "characters": ["C01"],
                "location": "LOC01",
                "must_show": ["the second light"],
                "must_not_show": [],
                "continuity": ["grey oilskin coat"],
                "beat": "reveal",
            },
            "visual": {"prompt": "A second light glows on black water", "shot": "close-up", "motion": "static", "text_placement": "lower_third"},
            "image": asset(seed=12),
        },
    ],
    "lines": [
        _line("L001", "narrator", "Every night for eleven years.", 250),
        _line("L002", "C01", "Every single night.", 0),
        _line("L003", "C01", "No. [sigh] Not again.", 400, whisper=True),
    ],
    "research": None,
    "source_work": None,
    "learnings_applied": [],
    "output": {"video": None, "captions": None, "contact_sheet": None, "qc": None},
}


def make_story(**overrides) -> dict:
    story = copy.deepcopy(BASE)
    story.update(copy.deepcopy(overrides))
    return story


def write_project(root: Path, story: dict) -> Path:
    """Write the canon skeleton (when the story has one) and the production folder."""
    canon = story.get("canon")
    if canon:
        canon_dir = root / canon["path"]
        (canon_dir / "scenes").mkdir(parents=True, exist_ok=True)
        (canon_dir / "chapters").mkdir(parents=True, exist_ok=True)
        (canon_dir / "story.md").write_text("---\ntitle: Demo\n---\n", encoding="utf-8")
        for chapter in canon["chapters"]:
            (canon_dir / "chapters" / f"{chapter}.md").write_text("---\n---\n", encoding="utf-8")
        for slide in story["slides"]:
            if slide.get("source"):
                (canon_dir / "scenes" / f"{slide['source']}.md").write_text("---\n---\n", encoding="utf-8")
    project = root / "projects" / story["slug"]
    project.mkdir(parents=True, exist_ok=True)
    (project / "story.json").write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")
    return project


def sine_wav_bytes(ms: int, rate: int = 24000, freq: float = 440.0) -> bytes:
    count = round(rate * ms / 1000)
    frames = b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * freq * i / rate))) for i in range(count))
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(frames)
    return buffer.getvalue()
