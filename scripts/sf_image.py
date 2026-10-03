#!/usr/bin/env python3
"""Generate character plates, location plates, and slide images through the image provider."""
from __future__ import annotations

import json
import subprocess
import time
import zlib
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

from sflib.project import (
    EXIT_BUG, EXIT_HUMAN, EXIT_OK, EXIT_PROVIDER, ProviderError, file_hash, input_hash,
    load_config, load_story, log, main_wrapper, needs_work, save_story, wanted,
)

SIZES = {"1:1": (1024, 1024), "3:4": (768, 1024), "9:16": (1080, 1920), "16:9": (1920, 1080)}
PLATE_ASPECT = {"face": "1:1", "half": "3:4", "full": "9:16"}
TRANSIENT_RETRIES = 3
QUALITY_RETRIES = 2
ERROR_CODES = {"quota", "auth", "content_blocked", "transient", "invalid"}


class QualityError(Exception):
    """The provider returned a file we cannot use; the item needs a human or a new prompt."""


class FakeProvider:
    name = "fake"

    def generate(self, prompt: str, aspect: str, refs: list[Path], seed: int | None, out: Path) -> None:
        width, height = SIZES[aspect]
        rgb = zlib.crc32(out.stem.encode()) & 0xFFFFFF
        image = Image.new("RGB", (width, height), ((rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255))
        font = ImageFont.load_default(size=max(24, width // 8))
        ImageDraw.Draw(image).text((width // 2, height // 2), out.stem, fill="white", anchor="mm",
                                   font=font, stroke_width=4, stroke_fill="black")
        out.parent.mkdir(parents=True, exist_ok=True)
        image.save(out)


class CommandProvider:
    name = "command"

    def __init__(self, command: list[str], timeout_s: int, prompt_dir: Path):
        self.command = command
        self.timeout_s = timeout_s
        self.prompt_dir = prompt_dir

    def generate(self, prompt: str, aspect: str, refs: list[Path], seed: int | None, out: Path) -> None:
        self.prompt_dir.mkdir(parents=True, exist_ok=True)
        prompt_file = self.prompt_dir / f"{out.stem}.txt"
        prompt_file.write_text(prompt, encoding="utf-8")
        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [*self.command, "--prompt-file", str(prompt_file), "--aspect", aspect, "--out", str(out)]
        for ref in refs:
            cmd += ["--ref", str(ref)]
        if seed is not None:
            cmd += ["--seed", str(seed)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout_s)
        except subprocess.TimeoutExpired as exc:
            raise ProviderError("transient", f"timed out after {self.timeout_s}s") from exc
        if proc.returncode != 0:
            raise parse_failure(proc.stderr)
        if not out.exists():
            raise ProviderError("invalid", "provider exited 0 but wrote no file")


def parse_failure(stderr: str) -> ProviderError:
    for raw in reversed(stderr.strip().splitlines()):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("error") in ERROR_CODES:
            return ProviderError(data["error"], str(data.get("message", "")))
    return ProviderError("transient", stderr.strip()[-500:] or "provider failed without a message")


def make_provider(config: dict, project_dir: Path):
    image = config["image"]
    if image["provider"] == "fake":
        return FakeProvider()
    if image["provider"] == "command":
        return CommandProvider(image["command"], int(image.get("timeout_s", 1200)), project_dir / "prompts")
    raise ValueError(f"unknown image provider {image['provider']!r}")


def check_image(path: Path, aspect: str) -> None:
    width, height = SIZES[aspect]
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            got_w, got_h = image.size
    except Exception as exc:  # any decoder failure means the file is unusable
        raise QualityError(f"{path.name} is not a readable image: {exc}") from exc
    expected = width / height
    if abs(got_w / got_h - expected) > 0.02 * expected:
        raise QualityError(f"{path.name} is {got_w}x{got_h}, expected aspect {aspect}")


def _generate_with_retries(provider, prompt, aspect, refs, seed, out, sleep: Callable[[float], None]) -> None:
    for attempt in range(TRANSIENT_RETRIES + 1):
        try:
            provider.generate(prompt, aspect, refs, seed, out)
            return
        except ProviderError as exc:
            if exc.code != "transient" or attempt == TRANSIENT_RETRIES:
                raise
            sleep(2 ** attempt)


def _plate_jobs(story: dict) -> list[tuple[str, dict, str, str]]:
    """(item id, plate entry, aspect, relative output path) for every character and location plate."""
    jobs = []
    for member in story["cast"]:
        for kind, plate in (member.get("plates") or {}).items():
            item = f"{member['id']}_{kind}"
            jobs.append((item, plate, PLATE_ASPECT[kind], f"plates/{item}.png"))
    for location in story["locations"]:
        jobs.append((location["id"], location["plate"], story["brief"]["aspect"], f"plates/{location['id']}.png"))
    return jobs


def _missing_plates(story: dict, slide: dict) -> list[str]:
    cast = {member["id"]: member for member in story["cast"]}
    locations = {location["id"]: location for location in story["locations"]}
    missing = []
    for character in slide["brief"]["characters"]:
        plates = cast[character].get("plates")
        if plates and plates["face"].get("status") != "done":
            missing.append(f"{character}_face")
    location = slide["brief"]["location"]
    if location and locations[location]["plate"].get("status") != "done":
        missing.append(location)
    return missing


def _slide_refs(story: dict, slide: dict, max_refs: int) -> list[str]:
    cast = {member["id"]: member for member in story["cast"]}
    locations = {location["id"]: location for location in story["locations"]}
    refs = []
    # Single-Hero Plate Injection (T020): Inject at most ONE character plate to prevent cross-blending
    for character in slide["brief"]["characters"]:
        plates = cast.get(character, {}).get("plates")
        if plates and plates.get("face", {}).get("path"):
            refs.append(plates["face"]["path"])
            break
    loc_id = slide["brief"].get("location")
    if loc_id and locations.get(loc_id):
        loc_plate = locations[loc_id].get("plate", {})
        if loc_plate.get("path"):
            refs.append(loc_plate["path"])
    return refs[:max_refs]


def run(project_dir: Path, only: set[str] | None = None, config: dict | None = None,
        sleep: Callable[[float], None] = time.sleep) -> tuple[dict, int]:
    config = config or load_config()
    provider = make_provider(config, project_dir)
    max_refs = int(config["image"].get("max_refs", 4))
    story = load_story(project_dir)
    summary: dict = {"done": [], "skipped": 0, "needs_human": [], "blocked": [], "errors": []}

    def process(item: str, entry: dict, prompt: str, aspect: str, refs: list[str], seed: int | None, rel_path: str) -> None:
        if not wanted(item, only):
            return
        new_hash = input_hash({"prompt": prompt, "aspect": aspect, "provider": provider.name, "seed": seed,
                               "refs": [file_hash(project_dir / ref) for ref in refs]})
        if only is None and not needs_work(entry, new_hash, project_dir):
            summary["skipped"] += 1
            return
        if entry.get("input_hash") != new_hash:
            entry["attempts"] = 0
        out = project_dir / rel_path
        last_quality_error = None
        for quality_attempt in range(QUALITY_RETRIES + 1):
            try:
                _generate_with_retries(provider, prompt, aspect, [project_dir / ref for ref in refs], seed, out, sleep)
                check_image(out, aspect)
                # Success: mark as done
                entry.update(status="done", path=rel_path, input_hash=new_hash, last_error=None)
                summary["done"].append(item)
                entry["attempts"] = entry.get("attempts", 0) + 1
                log(project_dir, "sf_image", f"{item}: {entry['status']} (attempt {entry['attempts']})")
                save_story(project_dir, story)
                return
            except ProviderError as exc:
                if exc.code in ("quota", "auth", "invalid"):
                    raise
                # content_blocked or transient exhausted: mark needs_human immediately
                entry.update(status="needs_human", input_hash=new_hash, last_error=f"{exc.code}: {exc.message}")
                summary["needs_human"].append(item)
                entry["attempts"] = entry.get("attempts", 0) + 1
                log(project_dir, "sf_image", f"{item}: {entry['status']} (attempt {entry['attempts']})")
                save_story(project_dir, story)
                return
            except QualityError as exc:
                last_quality_error = str(exc)
                if quality_attempt < QUALITY_RETRIES:
                    entry["attempts"] = entry.get("attempts", 0) + 1
                    continue
        # All quality retries exhausted
        entry.update(status="needs_human", input_hash=new_hash, last_error=last_quality_error)
        summary["needs_human"].append(item)
        entry["attempts"] = entry.get("attempts", 0) + 1
        log(project_dir, "sf_image", f"{item}: {entry['status']} (attempt {entry['attempts']})")
        save_story(project_dir, story)

    try:
        for item, plate, aspect, rel_path in _plate_jobs(story):
            process(item, plate, plate["prompt"], aspect, [], None, rel_path)
        for slide in story["slides"]:
            missing = _missing_plates(story, slide)
            if missing:
                if wanted(slide["id"], only):
                    summary["blocked"].append(f"{slide['id']} waits for {', '.join(missing)}")
                continue
            process(slide["id"], slide["image"], slide["visual"]["prompt"], story["brief"]["aspect"],
                    _slide_refs(story, slide, max_refs), slide["image"].get("seed"), f"images/{slide['id']}.png")
    except ProviderError as exc:
        save_story(project_dir, story)
        summary["errors"].append(f"{exc.code}: {exc.message}")
        return summary, EXIT_PROVIDER if exc.code in ("quota", "auth") else EXIT_BUG
    return summary, EXIT_HUMAN if summary["needs_human"] or summary["blocked"] else EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
