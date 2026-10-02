#!/usr/bin/env python3
"""Manage, inspect, and scaffold multi-channel workspaces in channels/."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from sflib.project import EXIT_HUMAN, EXIT_OK, ROOT

REQUIRED_MODULES = [
    "blueprint.md",
    "style-bible.md",
    "narrative-dna.md",
    "thumbnail-system.md",
    "voice-profile.md",
    "taste.md",
]


def get_channels_dir() -> Path:
    return ROOT / "channels"


def list_channels() -> list[dict]:
    channels_dir = get_channels_dir()
    if not channels_dir.exists():
        return []

    channels = []
    for item in sorted(channels_dir.iterdir()):
        if not item.is_dir() or item.name.startswith((".", "_")):
            continue
        missing = [mod for mod in REQUIRED_MODULES if not (item / mod).exists()]
        blueprint_file = item / "blueprint.md"
        name = item.name.replace("-", " ").title()
        niche = "N/A"
        if blueprint_file.exists():
            content = blueprint_file.read_text(encoding="utf-8")
            m_title = re.search(r"^#\s*Channel Blueprint:\s*(.+)$", content, re.MULTILINE)
            if m_title:
                name = m_title.group(1).strip()
            m_name = re.search(r"(?:Tên kênh \(Brand Name\)|Brand Name):\s*\*{0,2}([^\*\n\r]+)\*{0,2}", content)
            if m_name and m_name.group(1).strip():
                name = m_name.group(1).strip()
            m_niche = re.search(r"(?:Ngách nội dung|Niche Category):\s*([^\n\r]+)", content)
            if m_niche:
                niche = m_niche.group(1).strip().strip("*").strip()

        try:
            rel_path = str(item.relative_to(ROOT))
        except ValueError:
            rel_path = str(item)

        channels.append({
            "slug": item.name,
            "name": name,
            "niche": niche,
            "path": rel_path,
            "modules_present": len(REQUIRED_MODULES) - len(missing),
            "total_modules": len(REQUIRED_MODULES),
            "missing_modules": missing,
            "status": "valid" if not missing else "incomplete"
        })
    return channels


def scaffold_channel(slug: str, name: str = "", niche: str = "", language: str = "en") -> tuple[dict, int]:
    clean_slug = re.sub(r"[^a-z0-9-]", "-", slug.lower()).strip("-")
    if not clean_slug:
        return {"ok": False, "error": "Invalid channel slug"}, EXIT_HUMAN

    channels_dir = get_channels_dir()
    target_dir = channels_dir / clean_slug
    template_dir = channels_dir / "_template"

    if target_dir.exists():
        return {"ok": False, "error": f"Channel directory '{target_dir.name}' already exists"}, EXIT_HUMAN

    if not template_dir.exists():
        return {"ok": False, "error": "Template directory 'channels/_template' not found"}, EXIT_HUMAN

    target_name = name or clean_slug.replace("-", " ").title()
    target_niche = niche or "High-retention storytelling"

    # Copy template tree
    shutil.copytree(template_dir, target_dir)
    (target_dir / "assets").mkdir(parents=True, exist_ok=True)

    # Perform text replacements across copied markdown files
    for mod in REQUIRED_MODULES:
        file_path = target_dir / mod
        if file_path.exists():
            text = file_path.read_text(encoding="utf-8")
            text = text.replace("[Tên Kênh]", target_name)
            text = text.replace("[channel-slug]", clean_slug)
            text = text.replace("[PREFIX]", "".join([w[0].upper() for w in clean_slug.split("-")[:3]]))
            if mod == "blueprint.md":
                text = text.replace("[Ngách Nội Dung]", target_niche)
            if mod == "voice-profile.md" and language:
                text = text.replace("[English / Vietnamese / v.v.]", "English" if language == "en" else "Vietnamese")
            file_path.write_text(text, encoding="utf-8")

    try:
        rel_target = str(target_dir.relative_to(ROOT))
    except ValueError:
        rel_target = str(target_dir)

    return {
        "ok": True,
        "slug": clean_slug,
        "name": target_name,
        "path": rel_target,
        "files_created": REQUIRED_MODULES,
        "status": "created"
    }, EXIT_OK


def validate_channel(slug: str | None = None) -> tuple[dict, int]:
    channels = list_channels()
    if slug:
        filtered = [c for c in channels if c["slug"] == slug]
        if not filtered:
            return {"ok": False, "error": f"Channel '{slug}' not found"}, EXIT_HUMAN
        channels = filtered

    all_valid = all(c["status"] == "valid" for c in channels)
    return {
        "ok": all_valid,
        "channels": channels,
        "errors": [f"{c['slug']}: missing {c['missing_modules']}" for c in channels if c["missing_modules"]]
    }, EXIT_OK if all_valid else EXIT_HUMAN


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage StoryForge multi-channel workspaces")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # list
    subparsers.add_parser("list", help="List all configured channels")

    # new
    new_parser = subparsers.add_parser("new", help="Scaffold a new channel from _template")
    new_parser.add_argument("slug", help="Channel slug (e.g. tech-unfolded)")
    new_parser.add_argument("--name", default="", help="Display name of the channel")
    new_parser.add_argument("--niche", default="", help="Channel niche description")
    new_parser.add_argument("--lang", default="en", help="Primary language (en/vi)")

    # validate
    val_parser = subparsers.add_parser("validate", help="Validate channel module integrity")
    val_parser.add_argument("slug", nargs="?", default=None, help="Optional specific channel slug to validate")

    args = parser.parse_args()

    if args.subcommand == "list":
        channels = list_channels()
        print(json.dumps({"ok": True, "channels": channels}, ensure_ascii=False, indent=2))
        sys.exit(EXIT_OK)

    elif args.subcommand == "new":
        result, code = scaffold_channel(args.slug, name=args.name, niche=args.niche, language=args.lang)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(code)

    elif args.subcommand == "validate":
        result, code = validate_channel(args.slug)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(code)


if __name__ == "__main__":
    main()
