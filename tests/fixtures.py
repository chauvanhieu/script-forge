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


def _tone_frames(ms: int, rate: int = 24000, freq: float = 440.0) -> bytes:
    count = round(rate * ms / 1000)
    return b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * freq * i / rate))) for i in range(count))


def _silence_frames(ms: int, rate: int = 24000) -> bytes:
    return b"\x00\x00" * round(rate * ms / 1000)


def _wav_bytes(frames: bytes, rate: int = 24000) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(frames)
    return buffer.getvalue()


def sine_wav_bytes(ms: int, rate: int = 24000, freq: float = 440.0) -> bytes:
    return _wav_bytes(_tone_frames(ms, rate, freq), rate)


def silence_wav_bytes(ms: int, rate: int = 24000) -> bytes:
    return _wav_bytes(_silence_frames(ms, rate), rate)


def padded_tone_wav_bytes(lead_ms: int, tone_ms: int, trail_ms: int, rate: int = 24000, freq: float = 440.0) -> bytes:
    """tone_ms of audible tone flanked by lead_ms/trail_ms of silence -- simulates an untrimmed VoiceStudio take."""
    frames = _silence_frames(lead_ms, rate) + _tone_frames(tone_ms, rate, freq) + _silence_frames(trail_ms, rate)
    return _wav_bytes(frames, rate)


class FakeVS:
    """In-memory VoiceStudio: sine WAVs (1000 ms unless durations[text] says otherwise), transcripts echo the text."""

    def __init__(self, bad_transcripts: int = 0, fail_generate: str | None = None, fail_after: int = 0,
                 durations: dict[str, int] | None = None, padded: dict[str, tuple[int, int]] | None = None):
        self.calls: list[dict] = []
        self.bad_left = bad_transcripts
        self.fail_generate = fail_generate
        self.fail_after = fail_after
        self.durations = durations or {}
        self.padded = padded or {}  # text -> (lead_ms, trail_ms) of silence around the tone, for trim tests
        self.profiles = 0
        self.design_ref_texts: list[str] = []

    def health(self):
        return None

    def describe(self, description):
        return {"attrs": {"Gender": "female"}, "instruct": "female"}

    def create_design_profile(self, name, attrs, instruct, language, ref_text=""):
        self.profiles += 1
        self.design_ref_texts.append(ref_text)
        return f"p{self.profiles}"

    def create_clone_profile(self, name, ref_audio, ref_text, language):
        Path(ref_audio).read_bytes()
        self.profiles += 1
        return f"p{self.profiles}"

    def generate(self, *, text, language, profile_id, seed, engine=None, instruct=None):
        self.calls.append({"text": text, "seed": seed, "instruct": instruct, "profile_id": profile_id, "language": language})
        if self.fail_generate and len(self.calls) > self.fail_after:
            from sflib.project import ProviderError
            raise ProviderError(self.fail_generate, "refused")
        ms = self.durations.get(text, 1000)
        lead, trail = self.padded.get(text, (0, 0))
        data = padded_tone_wav_bytes(lead, ms, trail) if lead or trail else sine_wav_bytes(ms)
        return data, {"seed": str(seed), "duration_s": str((lead + ms + trail) / 1000), "dropped_chunks": None}

    def transcribe_words(self, wav, language):
        from sflib.text import display_text
        if self.bad_left > 0:
            self.bad_left -= 1
            return [{"text": "zzz qqq", "start": 0.0, "end": 0.5}]
        text = self.calls[-1]["text"]
        words = display_text(text).split()
        step = self.durations.get(text, 1000) / 1000 / max(len(words), 1)
        return [{"text": w, "start": i * step, "end": (i + 1) * step} for i, w in enumerate(words)]


def prepare_media(root: Path, story: dict, durations: list[int]) -> Path:
    """Write the project, fake images for every plate/slide, sine WAVs, and approx words for every line."""
    import sf_align
    import sf_image
    from sflib.project import load_story, save_story
    from sflib.text import tokens

    project = write_project(root, story)
    sf_image.run(project, config={"image": {"provider": "fake", "max_refs": 4}})
    story = load_story(project)
    (project / "audio").mkdir(exist_ok=True)
    for line, ms in zip(story["lines"], durations):
        rel = f"audio/{line['id']}.wav"
        (project / rel).write_bytes(sine_wav_bytes(ms))
        line["audio"].update(status="done", path=rel, duration_ms=ms, input_hash=f"h-{line['id']}")
        line["words"] = sf_align.align_line(tokens(line["text"], story["brief"]["language"]), [], ms, story["brief"]["language"])
        line["words_hash"] = f"h-{line['id']}"
    save_story(project, story)
    return project
