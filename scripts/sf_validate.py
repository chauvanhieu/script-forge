#!/usr/bin/env python3
"""Validate a production's story.json: JSON schema, then cross references."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from sflib.project import EXIT_HUMAN, EXIT_OK, ROOT, load_story, main_wrapper, save_story
from sflib.text import invalid_tags

SCHEMA_PATH = ROOT / "schemas" / "story.schema.json"

STAGE_ALIASES = {
    "script": "gate1",
    "voiceover": "voice",
    "audio": "voice",
    "image": "images",
    "plate": "images",
    "video": "render",
}


def auto_heal_story(project_dir: Path, story: dict) -> bool:
    """Auto-heal common schema stage aliases and missing state structures."""
    modified = False
    state = story.get("state")
    if isinstance(state, dict):
        current_stage = state.get("stage")
        if current_stage in STAGE_ALIASES:
            state["stage"] = STAGE_ALIASES[current_stage]
            modified = True
    if modified:
        save_story(project_dir, story)
    return modified


def schema_errors(story: dict) -> list[str]:
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    found = sorted(validator.iter_errors(story), key=lambda e: [str(p) for p in e.absolute_path])
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}" for e in found]


def _duplicates(kind: str, ids: list[str]) -> list[str]:
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    return [f"duplicate {kind} ids: {', '.join(dupes)}"] if dupes else []


def _factual_errors(story: dict) -> list[str]:
    research = story.get("research")
    if not research:
        return ["factual content requires research"]
    errors: list[str] = []
    notes = {n["id"] for n in research["notes"]}
    claims = {c["id"]: c for c in research["claims"]}
    for claim in research["claims"]:
        for note_id in claim["note_ids"]:
            if note_id not in notes:
                errors.append(f"{claim['id']}: note '{note_id}' is not in research.notes")
    for line in story["lines"]:
        for claim_id in line["claim_ids"]:
            claim = claims.get(claim_id)
            if claim is None:
                errors.append(f"{line['id']}: claim '{claim_id}' is not in research.claims")
            elif claim["status"] == "unverified":
                errors.append(f"{line['id']}: claim '{claim_id}' is unverified; verify it or remove it before Gate 1")
    return errors


def _canon_errors(story: dict, root: Path) -> list[str]:
    canon = story.get("canon")
    if not canon:
        return [f"{story['brief']['content_type']} content requires canon"]
    canon_dir = root / canon["path"]
    if not (canon_dir / "story.md").exists():
        return [f"canon.path '{canon['path']}' has no story.md"]
    errors: list[str] = []
    for chapter in canon["chapters"]:
        if not (canon_dir / "chapters" / f"{chapter}.md").exists():
            errors.append(f"canon chapter '{chapter}' not found")
    for slide in story["slides"]:
        source = slide.get("source")
        if source is None:
            continue
        if not (canon_dir / "scenes" / f"{source}.md").exists():
            errors.append(f"{slide['id']}: source scene '{source}' not found in canon")
        elif source.split("-scene-")[0] not in canon["chapters"]:
            errors.append(f"{slide['id']}: source scene '{source}' is not in canon.chapters")
    return errors


def _physics_and_consistency_errors(story: dict) -> list[str]:
    errors: list[str] = []
    slide_ids = {s["id"] for s in story.get("slides", [])}

    for slide in story.get("slides", []):
        sid = slide["id"]
        brief = slide.get("brief", {})
        physics = brief.get("spatial_physics")
        if physics and isinstance(physics, dict):
            if physics.get("has_mechanical_action"):
                pair_type = physics.get("shot_pair_type")
                paired_id = physics.get("paired_slide_id")
                if pair_type in ("trigger_setup", "vector_threat"):
                    if not paired_id or paired_id not in slide_ids or paired_id == sid:
                        errors.append(
                            f"{sid}: spatial_physics has shot_pair_type '{pair_type}' but paired_slide_id "
                            f"'{paired_id}' is missing, invalid, or self-referencing"
                        )
                if not physics.get("contact_point") and not physics.get("force_direction"):
                    errors.append(
                        f"{sid}: spatial_physics with has_mechanical_action=True requires at least contact_point or force_direction"
                    )
    return errors


def reference_errors(story: dict, root: Path) -> list[str]:
    cast_ids = [c["id"] for c in story["cast"]]
    location_ids = [loc["id"] for loc in story["locations"]]
    line_ids = [line["id"] for line in story["lines"]]
    slide_ids = [slide["id"] for slide in story["slides"]]
    errors = (
        _duplicates("cast", cast_ids) + _duplicates("location", location_ids)
        + _duplicates("line", line_ids) + _duplicates("slide", slide_ids)
    )
    flattened = [lid for slide in story["slides"] for lid in slide["line_ids"]]
    deduped = []
    for lid in flattened:
        if not deduped or deduped[-1] != lid:
            deduped.append(lid)
    if deduped != line_ids:
        errors.append("slides' line_ids, concatenated in slide order, must equal the lines array order exactly "
                      "(each line must appear in lines array order without skipping or reordering)")
    for line in story["lines"]:
        if line["speaker"] not in cast_ids:
            errors.append(f"{line['id']}: speaker '{line['speaker']}' is not in cast")
        bad = invalid_tags(line["text"])
        if bad:
            errors.append(f"{line['id']}: unsupported bracket tags {bad}; allowed are the expressive tags and [[written|spoken]]")
    for slide in story["slides"]:
        for character in slide["brief"]["characters"]:
            if character not in cast_ids:
                errors.append(f"{slide['id']}: character '{character}' is not in cast")
        location = slide["brief"]["location"]
        if location is not None and location not in location_ids:
            errors.append(f"{slide['id']}: location '{location}' is not in locations")
    content_type = story["brief"]["content_type"]
    errors += _factual_errors(story) if content_type == "factual" else _canon_errors(story, root)
    if content_type == "adaptation" and not (story.get("source_work") or {}).get("rights_basis"):
        errors.append("adaptation requires source_work.rights_basis")
    errors += _physics_and_consistency_errors(story)
    return errors


def run(project_dir: Path, only: set[str] | None = None, root: Path = ROOT) -> tuple[dict, int]:
    story = load_story(project_dir)
    auto_heal_story(project_dir, story)
    errors = schema_errors(story) or reference_errors(story, root)
    return {"errors": errors}, EXIT_OK if not errors else EXIT_HUMAN


if __name__ == "__main__":
    main_wrapper(run, __doc__)
