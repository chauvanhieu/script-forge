#!/usr/bin/env python3
"""Initialize a new StoryForge project with directory scaffolding and a valid skeleton story.json."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
import sys
from pathlib import Path

from sflib.project import EXIT_OK, ROOT, input_hash, save_story


def parse_slug(name_or_path: str) -> str:
    path = Path(name_or_path)
    slug = path.name
    # remove non-alphanumeric except hyphen
    slug = re.sub(r"[^a-z0-9-]", "-", slug.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "untitled-story"


def build_skeleton_story(slug: str, content_type: str = "factual", aspect: str = "9:16",
                         language: str = "vi", target_seconds: int = 60, idea: str = "",
                         channel: str = "") -> dict:
    hook_text = "Điều kỳ lạ này có thể thay đổi hoàn toàn cách bạn nhìn nhận vấn đề." if language == "vi" else "This counterintuitive truth changes everything."
    
    research = {
        "notes": [
            {
                "id": "R01",
                "title": "Initial Topic Reference",
                "sources": ["Scientific Literature / Verified Reference"],
                "status": "verified",
                "accuracy": "must-be-accurate",
                "confidence": "high",
                "checked_on": "2026-09-30",
                "risk": []
            }
        ],
        "claims": [
            {
                "id": "CL01",
                "text": "Core factual claim backing the hook of the story.",
                "status": "verified",
                "note_ids": ["R01"],
                "limitations": "Standard physiological or scientific constraints apply."
            }
        ]
    } if content_type == "factual" else None

    prompt_s01 = (
        "Cinematic macro illustration, dramatic chiaroscuro lighting, "
        "volumetric rim light, full-frame vertical 9:16 composition, "
        "no text, no letters, no logos, no watermarks"
    )

    clean_channel = parse_slug(channel) if channel else ""
    channel_author = clean_channel.replace("-", " ").title() if clean_channel else "StoryForge"

    brief_dict: dict = {
        "idea": idea or f"A high-retention {content_type} story on {slug.replace('-', ' ')}",
        "language": language,
        "aspect": aspect,
        "content_type": content_type,
        "genre": "health" if content_type == "factual" else "drama",
        "target_seconds": target_seconds,
        "captions": {
            "mode": "karaoke",
            "style": "karaoke-bold",
            "animation": "none"
        },
        "review_mode": "auto"
    }
    if clean_channel:
        brief_dict["channel"] = clean_channel

    cast_voice: dict = {
        "source": "design",
        "design_prompt": "female, young adult, moderate pitch",
        "instruct": "female, young adult, moderate pitch",
        "profile_id": None
    }
    caption_color = "#00F0FF"

    if clean_channel:
        vp_path = ROOT / "channels" / clean_channel / "voice-profile.md"
        if vp_path.exists():
            vp_text = vp_path.read_text(encoding="utf-8")
            m_profile = re.search(r'profile_id:\s*"([^"]+)"', vp_text)
            if m_profile:
                cast_voice["profile_id"] = m_profile.group(1)
            m_prompt = re.search(r'design_prompt:\s*"([^"]+)"', vp_text)
            if m_prompt:
                cast_voice["design_prompt"] = m_prompt.group(1)
                cast_voice["instruct"] = m_prompt.group(1)
            m_color = re.search(r'caption_color:\s*"([^"]+)"', vp_text)
            if m_color:
                caption_color = m_color.group(1)

    story: dict = {
        "schema_version": "1.0",
        "slug": slug,
        "canon": None,
        "brief": brief_dict,
        "state": {
            "stage": "brief",
            "gates": {
                "script": {"approved_at": None},
                "images": {"approved_at": None}
            }
        },
        "style_bible": {
            "medium": "hyperrealistic 3D cinematic scientific illustration and macro photography",
            "palette": [
                "deep navy",
                "bioluminescent amber",
                "cyan",
                "crimson"
            ],
            "lighting": "volumetric rim lighting with dramatic chiaroscuro",
            "composition": "dynamic macro close-ups, full-frame vertical 9:16 framing, continuous action without blank margins",
            "avoid": [
                "generated text",
                "letters",
                "numbers",
                "logos",
                "watermarks",
                "empty bottom margins",
                "deformed anatomy"
            ]
        },
        "cast": [
            {
                "id": "narrator",
                "canon_id": None,
                "name": "Người dẫn chuyện" if language == "vi" else "Narrator",
                "role": "narrator",
                "caption_color": caption_color,
                "voice": cast_voice
            }
        ],
        "locations": [],
        "slides": [
            {
                "id": "S01",
                "source": None,
                "line_ids": ["L001"],
                "brief": {
                    "moment": "Opening visual hook establishing immediate intrigue",
                    "characters": [],
                    "location": None,
                    "must_show": [],
                    "must_not_show": ["text"],
                    "continuity": [],
                    "beat": "setup"
                },
                "visual": {
                    "prompt": prompt_s01,
                    "shot": "close-up",
                    "motion": "push_in",
                    "text_placement": "lower_third"
                },
                "image": {
                    "path": "images/S01.png",
                    "input_hash": None,
                    "status": "pending",
                    "attempts": 0,
                    "last_error": None,
                    "seed": 42
                }
            }
        ],
        "lines": [
            {
                "id": "L001",
                "speaker": "narrator",
                "text": hook_text,
                "whisper": False,
                "pause_after_ms": 300,
                "claim_ids": ["CL01"] if content_type == "factual" else [],
                "audio": {
                    "path": "audio/L001.wav",
                    "input_hash": None,
                    "status": "pending",
                    "attempts": 0,
                    "last_error": None,
                    "duration_ms": None,
                    "seed": 42,
                    "qc": None,
                    "asr_words": None
                },
                "words": [],
                "words_hash": None
            }
        ],
        "research": research,
        "source_work": None,
        "learnings_applied": [],
        "seo": {
            "title": idea[:80] if idea else re.sub(r"^\d{8}(-\d{6})?-", "", slug).replace("-", " ").title(),
            "description": f"Khám phá sự thật đằng sau {re.sub(r'^\d{8}(-\d{6})?-', '', slug).replace('-', ' ')} cùng StoryForge.",
            "keywords": [re.sub(r"^\d{8}(-\d{6})?-", "", slug).replace("-", " "), content_type, "shorts", "storyforge"],
            "author": channel_author
        },
        "output": {
            "video": f"out/{re.sub(r'^\d{8}(-\d{6})?-', '', slug).strip('-')}.mp4",
            "captions": "out/captions.ass",
            "contact_sheet": "out/contact_sheet.png",
            "qc": "out/qc.json",
            "thumbnail": "out/thumbnail.jpg" if aspect == "9:16" else None,
            "thumbnail_16_9": "out/thumbnail_16_9.jpg" if aspect == "16:9" else None
        }
    }
    return story


def build_skeleton_script(slug: str, title: str) -> str:
    clean_title = re.sub(r"^\d{8}(-\d{6})?-", "", title)
    return f"""# Kịch bản: {clean_title}

- **Slug:** `{slug}`
- **Thể loại:** Sức khỏe & Khoa học thường thức (Factual)
- **Định dạng:** 9:16 (YouTube Shorts / TikTok / Reels)
- **Thời lượng mục tiêu:** 60s (~20-26 slide cuts, ~1.5s - 2.5s/slide)
- **Hook Archetype:** Archetype #4 (The Unbelievable Fact)

---

## 1. Cấu Trúc 3-Layer Hook (0.0s - 1.5s)
- **Verbal Hook (L001):** *\"...\"*
- **Visual Hook (S01):** *\"...\"*
- **Text Hook:** *\"...\"*

---

## 2. Retention Spine & Escalation Engine (But / Therefore)
- [Điền mạch truyện leo thang theo nguyên tắc Nhưng / Vì thế]

---

## 3. Danh sách phân cảnh chi tiết (Slides & Lines)
| Slide | Voice ID | Lời thoại | Visual Prompt | Motion |
|---|---|---|---|---|
| S01 | L001 | ... | ... | push_in |
"""


def init_project(target: Path, content_type: str = "factual", aspect: str = "9:16",
                 language: str = "vi", target_seconds: int = 60, idea: str = "", force: bool = False,
                 with_timestamp: bool = False, channel: str = "") -> tuple[dict, int]:
    project_dir = target if target.is_absolute() else (ROOT / target).resolve()
    dir_name = project_dir.name

    if with_timestamp and not re.match(r"^\d{8}(-\d{6})?-", dir_name):
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        clean_name = parse_slug(dir_name)
        project_dir = project_dir.parent / f"{ts}-{clean_name}"

    slug = parse_slug(project_dir.name)

    # Subdirectories
    for sub in ["audio", "images", "clips", "logs", "out", "prompts"]:
        (project_dir / sub).mkdir(parents=True, exist_ok=True)

    story_file = project_dir / "story.json"
    script_file = project_dir / "script.md"

    if story_file.exists() and not force:
        return {"ok": True, "slug": slug, "project": str(project_dir), "status": "already_exists"}, EXIT_OK

    story = build_skeleton_story(slug, content_type, aspect, language, target_seconds, idea, channel=channel)
    save_story(project_dir, story)

    if not script_file.exists() or force:
        title = idea[:60] if idea else slug.replace("-", " ").title()
        script_file.write_text(build_skeleton_script(slug, title), encoding="utf-8")

    return {"ok": True, "slug": slug, "project": str(project_dir), "status": "initialized"}, EXIT_OK


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize StoryForge project scaffolding and valid skeleton story.json")
    parser.add_argument("project_dir", type=Path, help="Path to projects/<slug>")
    parser.add_argument("--type", choices=["factual", "fiction", "adaptation"], default="factual", help="Content type")
    parser.add_argument("--aspect", choices=["9:16", "16:9"], default="9:16", help="Video aspect ratio")
    parser.add_argument("--language", default="vi", help="Audio/caption language (default: vi)")
    parser.add_argument("--seconds", type=int, default=60, help="Target duration in seconds (default: 60)")
    parser.add_argument("--idea", default="", help="Initial idea or premise")
    parser.add_argument("--channel", default="", help="Target channel slug (e.g. the-grey-verdict)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing story.json")
    parser.add_argument("--no-timestamp", action="store_true", help="Do not prepend timestamp to project directory")

    args = parser.parse_args()
    summary, code = init_project(
        args.project_dir,
        content_type=args.type,
        aspect=args.aspect,
        language=args.language,
        target_seconds=args.seconds,
        idea=args.idea,
        channel=args.channel,
        force=args.force,
        with_timestamp=not args.no_timestamp
    )
    print(json.dumps(summary, ensure_ascii=False))
    sys.exit(code)


if __name__ == "__main__":
    main()
