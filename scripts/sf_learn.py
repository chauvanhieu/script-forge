#!/usr/bin/env python3
"""Record a production run in library/runs/ and update library/calibration.json from measurements."""
from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path

from sflib.project import EXIT_HUMAN, EXIT_OK, ROOT, input_hash, load_story, main_wrapper
from sflib.text import display_text, norm

LIBRARY = ROOT / "library"
ALPHA = 0.2  # EWMA weight of each new line's speaking rate
STAGES = {"sf_image": ("image", "done"), "sf_voice": ("voice_line", "done"), "sf_render": ("render", None)}

CHECK_SCOPES = {"script", "image", "audio", "captions"}
CHECK_CAP = 30
_TASTE_TAGS = {"global", "brief", "script", "visual", "audio", "captions", "9:16", "16:9"}
_TASTE = re.compile(r"^- (T\d{3,}) \[([^\]]+)\] (\S.*)$")
_SOURCE = re.compile(r'^  ← \S+ · \d{4}-\d{2}-\d{2} · ".+"$')
_CHECK = re.compile(r"^- (K\d{3,}) \[([^\]]+)\] (\S.*?)  hits: (\d+) · \S+$")


def speech_chars(text: str) -> int:
    return len("".join(norm(display_text(text)).split()))


def _taste_problems(lines: list[str]) -> list[str]:
    problems, seen = [], set()
    for index, raw in enumerate(lines):
        if not raw.startswith("- "):
            continue
        match = _TASTE.match(raw)
        if not match:
            problems.append(f"taste.md line {index + 1}: not '- T### [scope] rule': {raw!r}")
            continue
        rule_id, tags = match.group(1), [tag.strip() for tag in match.group(2).split("·")]
        if rule_id in seen:
            problems.append(f"taste.md {rule_id}: duplicate id")
        seen.add(rule_id)
        bad = [tag for tag in tags if tag not in _TASTE_TAGS and not re.fullmatch(r"[a-z][a-z0-9-]*", tag)]
        if bad:
            problems.append(f"taste.md {rule_id}: unknown scope tags {bad}")
        nxt = lines[index + 1] if index + 1 < len(lines) else ""
        if not _SOURCE.match(nxt):
            problems.append(f"taste.md {rule_id}: missing source line '  ← <slug> · YYYY-MM-DD · \"<user words>\"'")
    return problems


def _check_problems(lines: list[str]) -> list[str]:
    problems, seen, per_scope = [], set(), {}
    for index, raw in enumerate(lines):
        if not raw.startswith("- "):
            continue
        match = _CHECK.match(raw)
        if not match:
            problems.append(f"checks.md line {index + 1}: not '- K### [scope] check.  hits: N · slug/id': {raw!r}")
            continue
        check_id, tags = match.group(1), [tag.strip() for tag in match.group(2).split("·")]
        if check_id in seen:
            problems.append(f"checks.md {check_id}: duplicate id")
        seen.add(check_id)
        if tags[0] not in CHECK_SCOPES or len(tags) > 2 or (len(tags) == 2 and not re.fullmatch(r"[a-z]{2,3}", tags[1])):
            problems.append(f"checks.md {check_id}: scope must be one of {sorted(CHECK_SCOPES)} optionally '· <lang>'")
            continue
        per_scope[tags[0]] = per_scope.get(tags[0], 0) + 1
    problems += [f"checks.md: {scope} has {count} checks, cap is {CHECK_CAP}; drop the fewest-hit, oldest ones"
                 for scope, count in per_scope.items() if count > CHECK_CAP]
    return problems


def check_library(library_dir: Path) -> list[str]:
    problems = []
    for name, checker in (("taste.md", _taste_problems), ("checks.md", _check_problems)):
        path = library_dir / name
        if path.exists():
            problems += checker(path.read_text(encoding="utf-8").splitlines())
    return problems


def _read_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, path)


def _log_entries(project_dir: Path) -> list[dict]:
    path = project_dir / "logs" / "runs.jsonl"
    if not path.exists():
        return []
    return [json.loads(raw) for raw in path.read_text(encoding="utf-8").splitlines() if raw.strip()]


def _predicted_s(story: dict, rate: float | None) -> float | None:
    if not rate:
        return None
    chars = sum(speech_chars(line["text"]) for line in story["lines"])
    pauses = sum(line.get("pause_after_ms", 0) for line in story["lines"])
    return round(chars / rate + pauses / 1000, 2)


def run(project_dir: Path, only: set[str] | None = None, library_dir: Path = LIBRARY) -> tuple[dict, int]:
    story = load_story(project_dir)
    problems = check_library(library_dir)
    summary: dict = {"run_id": None, "recorded": False, "speaking_rate": {}, "library_problems": problems}
    history_path = library_dir / "runs" / f"{story['slug']}.json"
    history = _read_json(history_path, [])
    consumed = sum(entry["log_lines"] for entry in history)
    entries = _log_entries(project_dir)
    new = [entry for entry in entries[consumed:] if entry["script"] != "sf_learn"]
    if not new:
        return summary, EXIT_HUMAN if problems else EXIT_OK
    run_id = input_hash(new)
    summary["run_id"] = run_id
    if any(entry["run_id"] == run_id for entry in history):
        return summary, EXIT_HUMAN if problems else EXIT_OK
    calibration = _read_json(library_dir / "calibration.json", {"version": 1, "speaking_rate": {}, "stage_seconds": {}})
    lang = story["brief"]["language"].split("-")[0]
    rate_entry = calibration["speaking_rate"].get(lang)
    predicted = _predicted_s(story, rate_entry["chars_per_s"] if rate_entry else None)

    seen = {h for entry in history for h in entry["line_hashes"]}
    rates, hashes = [], []
    for line in story["lines"]:
        audio = line["audio"]
        chars = speech_chars(line["text"])
        if audio.get("status") != "done" or not audio.get("duration_ms") or not chars or audio["input_hash"] in seen:
            continue
        rates.append(chars / (audio["duration_ms"] / 1000))
        hashes.append(audio["input_hash"])
    if rates:
        if rate_entry is None:
            rate_entry = {"chars_per_s": sum(rates) / len(rates), "lines": len(rates)}
        else:
            for rate in rates:
                rate_entry["chars_per_s"] = (1 - ALPHA) * rate_entry["chars_per_s"] + ALPHA * rate
            rate_entry["lines"] += len(rates)
        calibration["speaking_rate"][lang] = rate_entry

    wall: dict[str, float] = {}
    for entry in new:
        wall[entry["script"]] = round(wall.get(entry["script"], 0.0) + entry["elapsed_s"], 3)
        stage = STAGES.get(entry["script"])
        if entry["exit"] != EXIT_OK or stage is None:
            continue
        key, count_field = stage
        count = entry["counts"].get(count_field, 0) if count_field else 1
        if count:
            slot = calibration["stage_seconds"].setdefault(key, {"mean": 0.0, "n": 0})
            slot["mean"] = round((slot["mean"] * slot["n"] + entry["elapsed_s"]) / (slot["n"] + count), 3)
            slot["n"] += count

    durations = [line["audio"].get("duration_ms") for line in story["lines"]]
    actual = None
    if all(durations):
        actual = round((sum(durations) + sum(line.get("pause_after_ms", 0) for line in story["lines"])) / 1000, 2)
    qc = _read_json(project_dir / "out" / "qc.json", {"checks": []})
    history.append({
        "run_id": run_id,
        "date": date.today().isoformat(),
        "log_lines": len(entries) - consumed,
        "line_hashes": hashes,
        "target_s": story["brief"]["target_seconds"],
        "actual_s": actual,
        "predicted_s": predicted,
        "images_generated": sum(e["counts"].get("done", 0) for e in new if e["script"] == "sf_image"),
        "voice_lines_generated": sum(e["counts"].get("done", 0) for e in new if e["script"] == "sf_voice"),
        "needs_human": sum(e["counts"].get("needs_human", 0) for e in new),
        "untrusted_timings": sum(e["counts"].get("untrusted_timings", 0) for e in new if e["script"] == "sf_align"),
        "qc_failed": [check["name"] for check in qc["checks"] if not check["ok"]],
        "stage_wall_s": wall,
    })
    _write_json(history_path, history)
    _write_json(library_dir / "calibration.json", calibration)
    summary.update(recorded=True, speaking_rate={k: round(v["chars_per_s"], 2) for k, v in calibration["speaking_rate"].items()})
    return summary, EXIT_HUMAN if problems else EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
