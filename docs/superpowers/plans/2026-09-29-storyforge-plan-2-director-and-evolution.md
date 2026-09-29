# StoryForge Plan 2: Director Skills and Evolution Loop — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One command (`/story`) turns an idea into a finished video; taste rules evolve only from user feedback (`/story-feedback`), while measured workflow knowledge (`calibration.json`, `checks.md`, `runs/`) updates automatically after every run.

**Architecture:** A small deterministic engine addition (`runs.jsonl` logging in `main_wrapper`, a new `sf_learn` script with a library validator) plus four lean Claude Code skills and three slash commands that orchestrate the existing `sf_*` scripts. Knowledge lives in `library/` as plain files the skills read on entry.

**Tech Stack:** Python ≥3.11 via `uv`, pytest; Markdown skills/commands for Claude Code (`.claude/skills`, `.claude/commands`).

**Spec:** `docs/superpowers/specs/2026-09-29-storyforge-director-and-evolution-design.md` (and the base spec `docs/superpowers/specs/2026-09-28-storyforge-design.md`).

## Global Constraints

- All code, comments, docs, skills and messages are in **English** (skills may quote user feedback verbatim in any language).
- Python `>=3.11`; run everything through `uv run` from the repo root `/Users/irondev/Desktop/Projects/chauvanhieu/yt`.
- Dependencies are exactly: `httpx`, `jsonschema`, `Pillow`, `PyYAML` (runtime) and `pytest` (dev). Add nothing.
- Script stdout is **exactly one JSON line**; exit codes `0` success, `1` bug, `2` needs human, `3` provider quota/auth.
- JSON writes to shared state are atomic (temp file + `os.replace`).
- `library/taste.md` is written **only** by the `/story-feedback` flow. `library/calibration.json` and `library/runs/*.json` are written **only** by `sf_learn`. `library/checks.md` is written by auto gates / QC handling in the skills.
- Commit messages end with the line `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## File Structure

```
scripts/sflib/project.py          # modify: main_wrapper appends logs/runs.jsonl
scripts/sf_learn.py               # create: run history, calibration, library validation
schemas/story.schema.json         # modify: review_mode gated|auto
tests/test_project.py             # modify: runs.jsonl test
tests/test_sf_learn.py            # create
library/taste.md                  # create: header only (no rules until feedback)
library/checks.md                 # create: seeded objective checks
library/calibration.json          # created by running sf_learn (Task 6)
library/runs/<slug>.json          # created by running sf_learn (Task 6)
.claude/commands/story.md         # create
.claude/commands/story-feedback.md
.claude/commands/story-redo.md
.claude/skills/sf-director/SKILL.md
.claude/skills/sf-director/references/services.md
.claude/skills/sf-director/references/feedback.md
.claude/skills/sf-script/SKILL.md
.claude/skills/sf-script/references/rubric.md
.claude/skills/sf-script/references/speaking-rates.md
.claude/skills/sf-visual/SKILL.md
.claude/skills/sf-audio/SKILL.md
docs/superpowers/specs/2026-09-28-storyforge-design.md   # modify (Task 6)
.gitignore                        # modify: /logs/
```

---

### Task 1: `runs.jsonl` logging and `review_mode: auto`

**Files:**
- Modify: `scripts/sflib/project.py` (`main_wrapper`, new `_record_run`)
- Modify: `schemas/story.schema.json:40`
- Test: `tests/test_project.py`, `tests/test_sf_validate.py`

**Interfaces:**
- Produces: every script invocation through `main_wrapper` appends one line to `<project>/logs/runs.jsonl`:
  `{"script": str, "started": "YYYY-MM-DDTHH:MM:SS+00:00", "elapsed_s": float, "exit": int, "counts": {<summary list field>: int}}`.
  Nothing is written when the project dir does not exist or when the lock was held by another process.
- Produces: `brief.review_mode` accepts `"gated"` or `"auto"`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_project.py` (it already has the `_main(monkeypatch, capsys, argv, run)` helper that returns `(code, summary, err)`):

```python
def test_main_wrapper_appends_one_runs_jsonl_line_per_invocation(tmp_path, monkeypatch, capsys):
    def run(project_dir, only):
        return {"done": ["L001", "L002"], "skipped": 0, "needs_human": []}, 0
    _main(monkeypatch, capsys, [str(tmp_path)], run)
    _main(monkeypatch, capsys, [str(tmp_path)], run)
    lines = (tmp_path / "logs" / "runs.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    entry = json.loads(lines[0])
    assert entry["script"] == "sf_demo" and entry["exit"] == 0
    assert entry["counts"] == {"done": 2, "needs_human": 0}
    assert entry["elapsed_s"] >= 0 and entry["started"].endswith("+00:00")


def test_main_wrapper_records_crashes_but_not_missing_projects(tmp_path, monkeypatch, capsys):
    def boom(project_dir, only):
        raise RuntimeError("x")
    _main(monkeypatch, capsys, [str(tmp_path)], boom)
    entry = json.loads((tmp_path / "logs" / "runs.jsonl").read_text(encoding="utf-8"))
    assert entry["exit"] == 1 and entry["counts"] == {"errors": 1}
    _main(monkeypatch, capsys, [str(tmp_path / "nope")], lambda project_dir, only: ({}, 0))
    assert not (tmp_path / "nope").exists()
```

Make sure `import json` is at the top of `tests/test_project.py` (add it if missing).

Append to `tests/test_sf_validate.py`:

```python
def test_review_mode_accepts_auto_and_rejects_unknown(tmp_path):
    story = make_story()
    story["brief"]["review_mode"] = "auto"
    assert sf_validate.schema_errors(story) == []
    story["brief"]["review_mode"] = "yolo"
    assert sf_validate.schema_errors(story) != []
```

(`sf_validate.schema_errors(story) -> list[str]` exists; add `from fixtures import make_story` / `import sf_validate` at the top if the file does not already import them.)

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_project.py tests/test_sf_validate.py -q`
Expected: the three new tests FAIL (no `runs.jsonl`; `"auto"` rejected by the schema).

- [ ] **Step 3: Implement**

In `schemas/story.schema.json`, replace `"review_mode": {"const": "gated"}` with:

```json
"review_mode": {"enum": ["gated", "auto"]}
```

In `scripts/sflib/project.py`, add `import time` and `from datetime import datetime, timezone` to the imports, add this function above `main_wrapper`, and replace `main_wrapper` with the version below:

```python
def _record_run(project_dir: Path, script: str, started: str, elapsed_s: float, code: int, summary: dict) -> None:
    """Append one measurement line for sf_learn; never let logging break a run."""
    if not project_dir.is_dir():
        return
    counts = {key: len(value) for key, value in summary.items() if isinstance(value, list)}
    entry = {"script": script, "started": started, "elapsed_s": round(elapsed_s, 3), "exit": code, "counts": counts}
    try:
        logs = project_dir / "logs"
        logs.mkdir(exist_ok=True)
        with (logs / "runs.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main_wrapper(run: Callable[..., tuple[dict, int]], description: str) -> NoReturn:
    args = _parse_args(description)
    script = Path(sys.argv[0]).stem
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    clock = time.monotonic()
    try:
        with project_lock(args.project_dir):
            summary, code = run(args.project_dir, args.only)
    except LockedError as exc:
        _emit({"errors": [str(exc)]}, EXIT_HUMAN)
    except Exception as exc:
        if args.project_dir.is_dir():
            log(args.project_dir, script, traceback.format_exc())
        else:
            sys.stderr.write(traceback.format_exc())
        summary, code = {"errors": [f"{type(exc).__name__}: {exc}"]}, EXIT_BUG
    _record_run(args.project_dir, script, started, time.monotonic() - clock, code, summary)
    _emit(summary, code)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_project.py tests/test_sf_validate.py -q` → all pass.
Run: `uv run pytest -q` → full suite passes (122 + 3 new).

- [ ] **Step 5: Commit**

```bash
git add scripts/sflib/project.py schemas/story.schema.json tests/test_project.py tests/test_sf_validate.py
git commit -m "$(cat <<'EOF'
Log every script run to logs/runs.jsonl; allow review_mode auto

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: `sf_learn` — run history and calibration

**Files:**
- Create: `scripts/sf_learn.py`
- Test: `tests/test_sf_learn.py`

**Interfaces:**
- Consumes: `logs/runs.jsonl` lines from Task 1; `sflib.project` (`ROOT`, `EXIT_OK`, `EXIT_HUMAN`, `input_hash`, `load_story`, `main_wrapper`); `sflib.text` (`display_text`, `norm`).
- Produces:
  - `sf_learn.LIBRARY = ROOT / "library"`, `sf_learn.ALPHA = 0.2`
  - `sf_learn.speech_chars(text: str) -> int` — display characters without spaces (same count `sf_voice` uses for `qc.cps`).
  - `sf_learn.run(project_dir: Path, only=None, library_dir: Path = LIBRARY) -> tuple[dict, int]`; summary `{"run_id": str | None, "recorded": bool, "speaking_rate": {lang: float}, "library_problems": [str]}`.
  - `sf_learn.check_library(library_dir: Path) -> list[str]` — **stub in this task that returns `[]`**; Task 3 implements it.
  - Files: `library/calibration.json` = `{"version": 1, "speaking_rate": {lang: {"chars_per_s": float, "lines": int}}, "stage_seconds": {"image"|"voice_line"|"render": {"mean": float, "n": int}}}`; `library/runs/<slug>.json` = list of entries `{"run_id", "date", "log_lines", "line_hashes", "target_s", "actual_s", "predicted_s", "images_generated", "voice_lines_generated", "needs_human", "untrusted_timings", "qc_failed", "stage_wall_s"}`.

- [ ] **Step 1: Write the failing tests**

`tests/test_sf_learn.py`:

```python
import json

from fixtures import make_story, write_project
import sf_learn
from sflib.project import load_story, save_story


def _voiced(tmp_path, durations=(1000, 700, 1300)):
    project = write_project(tmp_path / "work", make_story())
    story = load_story(project)
    for line, ms in zip(story["lines"], durations):
        line["audio"].update(status="done", path=f"audio/{line['id']}.wav", duration_ms=ms, input_hash=f"h-{line['id']}")
    save_story(project, story)
    return project


def _log(project, *entries):
    logs = project / "logs"
    logs.mkdir(exist_ok=True)
    with (logs / "runs.jsonl").open("a", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")


VOICE = {"script": "sf_voice", "started": "2026-09-29T10:00:00+00:00", "elapsed_s": 30.0, "exit": 0, "counts": {"done": 3}}
IMAGE = {"script": "sf_image", "started": "2026-09-29T10:01:00+00:00", "elapsed_s": 50.0, "exit": 0, "counts": {"done": 2}}
RENDER = {"script": "sf_render", "started": "2026-09-29T10:02:00+00:00", "elapsed_s": 12.0, "exit": 0, "counts": {"rendered": 2}}


def test_speech_chars_matches_display_text_without_spaces_or_tags():
    assert sf_learn.speech_chars("No. [sigh] Not again.") == len("No.Notagain.")
    assert sf_learn.speech_chars("[sigh]") == 0


def test_first_run_seeds_calibration_and_history(tmp_path):
    project = _voiced(tmp_path)
    _log(project, VOICE, IMAGE, RENDER)
    library = tmp_path / "library"
    summary, code = sf_learn.run(project, library_dir=library)
    assert code == 0 and summary["recorded"] is True
    cal = json.loads((library / "calibration.json").read_text())
    story = load_story(project)
    rates = [sf_learn.speech_chars(l["text"]) / (l["audio"]["duration_ms"] / 1000) for l in story["lines"]]
    assert cal["speaking_rate"]["en"]["lines"] == 3
    assert abs(cal["speaking_rate"]["en"]["chars_per_s"] - sum(rates) / 3) < 1e-6
    assert cal["stage_seconds"]["voice_line"] == {"mean": 10.0, "n": 3}
    assert cal["stage_seconds"]["image"] == {"mean": 25.0, "n": 2}
    assert cal["stage_seconds"]["render"] == {"mean": 12.0, "n": 1}
    history = json.loads((library / "runs" / f"{story['slug']}.json").read_text())
    assert len(history) == 1 and history[0]["run_id"] == summary["run_id"]
    assert history[0]["log_lines"] == 3 and sorted(history[0]["line_hashes"]) == ["h-L001", "h-L002", "h-L003"]
    assert history[0]["voice_lines_generated"] == 3 and history[0]["images_generated"] == 2
    expected_actual = (1000 + 700 + 1300 + sum(l["pause_after_ms"] for l in story["lines"])) / 1000
    assert history[0]["actual_s"] == round(expected_actual, 2)
    assert history[0]["predicted_s"] is None  # no calibration existed before this run


def test_rerun_without_new_log_lines_changes_nothing(tmp_path):
    project = _voiced(tmp_path)
    _log(project, VOICE)
    library = tmp_path / "library"
    sf_learn.run(project, library_dir=library)
    before = (library / "calibration.json").read_text()
    _log(project, {"script": "sf_learn", "started": "x", "elapsed_s": 0.1, "exit": 0, "counts": {}})
    summary, code = sf_learn.run(project, library_dir=library)
    assert code == 0 and summary["recorded"] is False
    assert (library / "calibration.json").read_text() == before


def test_second_run_uses_ewma_and_counts_each_line_hash_once(tmp_path):
    project = _voiced(tmp_path)
    _log(project, VOICE)
    library = tmp_path / "library"
    sf_learn.run(project, library_dir=library)
    old = json.loads((library / "calibration.json").read_text())["speaking_rate"]["en"]["chars_per_s"]
    story = load_story(project)
    story["lines"][0]["audio"].update(duration_ms=2000, input_hash="h-L001-v2")  # one line re-voiced
    save_story(project, story)
    _log(project, dict(VOICE, counts={"done": 1}))
    summary, _ = sf_learn.run(project, library_dir=library)
    cal = json.loads((library / "calibration.json").read_text())
    new_rate = sf_learn.speech_chars(story["lines"][0]["text"]) / 2.0
    assert cal["speaking_rate"]["en"]["lines"] == 4
    assert abs(cal["speaking_rate"]["en"]["chars_per_s"] - ((1 - sf_learn.ALPHA) * old + sf_learn.ALPHA * new_rate)) < 1e-6
    history = json.loads((library / "runs" / f"{story['slug']}.json").read_text())
    assert len(history) == 2 and history[1]["predicted_s"] is not None


def test_no_log_lines_records_nothing(tmp_path):
    project = _voiced(tmp_path)
    summary, code = sf_learn.run(project, library_dir=tmp_path / "library")
    assert code == 0 and summary == {"run_id": None, "recorded": False, "speaking_rate": {}, "library_problems": []}
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_sf_learn.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'sf_learn'`.

- [ ] **Step 3: Implement `scripts/sf_learn.py`**

```python
#!/usr/bin/env python3
"""Record a production run in library/runs/ and update library/calibration.json from measurements."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import date
from pathlib import Path

from sflib.project import EXIT_HUMAN, EXIT_OK, ROOT, input_hash, load_story, main_wrapper
from sflib.text import display_text, norm

LIBRARY = ROOT / "library"
ALPHA = 0.2  # EWMA weight of each new line's speaking rate
STAGES = {"sf_image": ("image", "done"), "sf_voice": ("voice_line", "done"), "sf_render": ("render", None)}


def speech_chars(text: str) -> int:
    return len("".join(norm(display_text(text)).split()))


def check_library(library_dir: Path) -> list[str]:
    return []  # implemented in Task 3


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
    _write_json(library_dir / "calibration.json", calibration)
    _write_json(history_path, history)
    summary.update(recorded=True, speaking_rate={k: round(v["chars_per_s"], 2) for k, v in calibration["speaking_rate"].items()})
    return summary, EXIT_HUMAN if problems else EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
```

Note on `log_lines`: it counts **all** consumed lines including `sf_learn`'s own, so the next run starts after them. In `test_rerun_without_new_log_lines_changes_nothing` the second call sees only an `sf_learn` line, so `new` is empty and nothing is written; `consumed` stays at 1, which is correct because a later real run will filter the `sf_learn` line out again.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_sf_learn.py -q` → 5 passed.
Run: `uv run pytest -q` → full suite passes.

- [ ] **Step 5: Commit**

```bash
git add scripts/sf_learn.py tests/test_sf_learn.py
git commit -m "$(cat <<'EOF'
Add sf_learn: run history and measured calibration

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Library validation (`check_library`) and library seed files

**Files:**
- Modify: `scripts/sf_learn.py` (`check_library`)
- Create: `library/taste.md`, `library/checks.md`
- Test: `tests/test_sf_learn.py`

**Interfaces:**
- Consumes: `sf_learn.run` calls `check_library(library_dir)` (Task 2).
- Produces: `check_library(library_dir: Path) -> list[str]` returning human-readable problems; formats below are the contract every skill writes.

Taste entry (two lines):
```
- T007 [vi · 9:16] Child voices must sound younger than described; prefer "child, high pitch".
  ← den-ong-sao · 2026-09-29 · "giọng Bống trẻ hơn nữa"
```
Check entry (one line; two spaces before `hits`):
```
- K004 [image] Moon scenes: state the count in the prompt ("exactly one full moon").  hits: 1 · den-ong-sao/S05
```
Check scopes: `script`, `image`, `audio`, `captions`, optionally ` · <lang>` (2–3 lowercase letters). Taste scope tags: one or more of `global`, `brief`, `script`, `visual`, `audio`, `captions`, an aspect (`9:16`, `16:9`), or a lowercase slug (language code or genre), separated by ` · `. At most 30 checks per scope (scope = the first tag).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_sf_learn.py`:

```python
GOOD_TASTE = """# Taste rules

- T001 [global · brief] Default to Vietnamese, 9:16, 60 seconds, karaoke-bold captions.
  ← den-ong-sao · 2026-09-29 · "mặc định tiếng Việt, shorts 1 phút"
"""
GOOD_CHECKS = """# Objective checks

- K001 [image] Moon scenes: state the count in the prompt ("exactly one full moon").  hits: 1 · den-ong-sao/S05
- K002 [audio · vi] Vietnamese ASR word timings are untrusted; expect approx karaoke.  hits: 16 · den-ong-sao/L001
"""


def _library(tmp_path, taste=GOOD_TASTE, checks=GOOD_CHECKS):
    library = tmp_path / "library"
    library.mkdir(exist_ok=True)
    (library / "taste.md").write_text(taste, encoding="utf-8")
    (library / "checks.md").write_text(checks, encoding="utf-8")
    return library


def test_check_library_accepts_valid_files_and_missing_files(tmp_path):
    assert sf_learn.check_library(_library(tmp_path)) == []
    assert sf_learn.check_library(tmp_path / "empty") == []


def test_check_library_rejects_malformed_entries(tmp_path):
    bad_taste = GOOD_TASTE + "- T001 [global] Duplicate id.\n  ← x · 2026-09-29 · \"y\"\n- T002 [global] Missing source line.\n"
    bad_checks = GOOD_CHECKS + "- K003 [pictures] Unknown scope.  hits: 1 · x/S01\n- K004 no brackets\n"
    problems = sf_learn.check_library(_library(tmp_path, bad_taste, bad_checks))
    assert any("T001" in p and "duplicate" in p for p in problems)
    assert any("T002" in p and "source" in p for p in problems)
    assert any("K003" in p and "scope" in p for p in problems)
    assert any("K004" in p or "no brackets" in p for p in problems)


def test_check_library_enforces_the_per_scope_cap(tmp_path):
    many = "".join(f"- K{i:03d} [image] Check {i}.  hits: 1 · x/S01\n" for i in range(1, 32))
    problems = sf_learn.check_library(_library(tmp_path, checks=many))
    assert any("image" in p and "30" in p for p in problems)


def test_library_problems_make_sf_learn_exit_2(tmp_path):
    project = _voiced(tmp_path)
    _log(project, VOICE)
    library = _library(tmp_path, checks="- K001 [pictures] x.  hits: 1 · a/S01\n")
    summary, code = sf_learn.run(project, library_dir=library)
    assert code == 2 and summary["library_problems"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_sf_learn.py -q`
Expected: the new rejection/cap/exit tests FAIL (stub returns `[]`).

- [ ] **Step 3: Implement `check_library` and add `import re`**

Replace the stub in `scripts/sf_learn.py` (add `import re` to the imports):

```python
CHECK_SCOPES = {"script", "image", "audio", "captions"}
CHECK_CAP = 30
_TASTE_TAGS = {"global", "brief", "script", "visual", "audio", "captions", "9:16", "16:9"}
_TASTE = re.compile(r"^- (T\d{3,}) \[([^\]]+)\] (\S.*)$")
_SOURCE = re.compile(r'^  ← \S+ · \d{4}-\d{2}-\d{2} · ".+"$')
_CHECK = re.compile(r"^- (K\d{3,}) \[([^\]]+)\] (\S.*?)  hits: (\d+) · \S+$")


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
```

- [ ] **Step 4: Create the library seed files**

`library/taste.md`:

```markdown
# Taste rules

Written only by `/story-feedback`, from the user's own feedback. Each rule is two lines:
`- T### [scope tags] rule` then `  ← <slug> · YYYY-MM-DD · "<the user's words>"`.
A rule that contradicts an older one of the same or broader scope replaces it (the old line is deleted and the new rule says "replaces T###").
```

`library/checks.md` (objective defects already found in `projects/den-ong-sao` and `projects/smoke-test`):

```markdown
# Objective checks

Written by auto gates and QC handling. One line per check:
`- K### [scope] check.  hits: N · <slug>/<id>`; scope is script, image, audio or captions, optionally `· <lang>`.
Bump `hits` (and the slug/id) when a check catches a defect again. At most 30 per scope.

- K001 [image] Night and moon scenes: state the exact count in the prompt ("exactly one round full moon, no crescent").  hits: 1 · den-ong-sao/S05
- K002 [image] Plate prompts named "face" must say "head-and-shoulders portrait, face fills the frame"; otherwise the model draws a full body.  hits: 1 · den-ong-sao/C01_face
- K003 [audio · vi] VoiceStudio's Vietnamese word aligner is untrusted; sf_align falls back to pause-anchored approx timings, so put punctuation where the voice should pause.  hits: 16 · den-ong-sao/L001
- K004 [script · vi] Budget Vietnamese lines with the measured speaking rate in library/calibration.json; the untuned estimate overshot 60 s by 7 %.  hits: 1 · den-ong-sao/L016
```

- [ ] **Step 5: Run the tests to verify they pass, then validate the seeds**

Run: `uv run pytest tests/test_sf_learn.py -q` → 9 passed.
Run: `uv run python -c "import sys; sys.path.insert(0, 'scripts'); import sf_learn; print(sf_learn.check_library(sf_learn.LIBRARY))"` → `[]`.
Run: `uv run pytest -q` → full suite passes.

- [ ] **Step 6: Commit**

```bash
git add scripts/sf_learn.py tests/test_sf_learn.py library/taste.md library/checks.md
git commit -m "$(cat <<'EOF'
Validate library taste and checks files; seed objective checks

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: `sf-director` skill and the three commands

**Files:**
- Create: `.claude/skills/sf-director/SKILL.md`, `.claude/skills/sf-director/references/services.md`, `.claude/skills/sf-director/references/feedback.md`
- Create: `.claude/commands/story.md`, `.claude/commands/story-feedback.md`, `.claude/commands/story-redo.md`
- Modify: `.gitignore` (add `/logs/`)

**Interfaces:**
- Consumes: scripts `sf_validate`, `sf_image`, `sf_contact_sheet`, `sf_voice`, `sf_align`, `sf_captions`, `sf_render`, `sf_qc`, `sf_learn` (all `uv run scripts/<name>.py projects/<slug> [--only ids]`); `library/taste.md`, `library/checks.md`, `library/calibration.json` formats (Task 3); skills `sf-script`, `sf-visual`, `sf-audio` (Task 5 — referenced by name).
- Produces: the orchestration contract the other skills follow (stages, gate rounds, where rules are read/written).

- [ ] **Step 1: Write `.claude/skills/sf-director/SKILL.md`**

```markdown
---
name: sf-director
description: Orchestrates a StoryForge production from idea to final video — stages, gates, resume, feedback. Entered by /story, /story-feedback and /story-redo; use it whenever a StoryForge production is created, resumed, redone or given feedback.
---

# sf-director

You run StoryForge productions in `/Users/irondev/Desktop/Projects/chauvanhieu/yt`.
Scripts do all mechanical work: `uv run scripts/<script>.py projects/<slug> [--only ids]`.
Each prints one JSON line; exit 0 ok, 1 bug, 2 needs human, 3 provider quota/auth.
Never edit fields scripts own (asset path/status/hash/attempts/last_error, audio measurements, words, output.*).

## On entry

1. Read `library/taste.md` and `library/checks.md`; keep only entries whose scope tags all
   match this production (language, aspect, genre, stage, or `global`). These are the rules.
2. Read `library/calibration.json` if it exists.
3. Record applied rule/check ids in `story.json` `learnings_applied` when the production exists.

## Stages (`/story`)

| # | Stage | Do | Exit |
|---|---|---|---|
| 1 | brief | Fill `brief` from the idea. Defaults come from taste rules scoped `brief`; with none: language `vi`, aspect `9:16`, `target_seconds` 60, captions `karaoke`/`karaoke-bold`, `review_mode` `auto`. Ask the user only if the idea gives no premise to write from. | brief complete |
| 2 | canon + script | Dispatch one subagent that follows `sf-script` (pass: brief, matching rules, calibration numbers, target paths). | `sf_validate` ok; Story CLI `validate`, `links` clean |
| 3 | Gate 1 | auto: score `script.md` against `sf-script/references/rubric.md` and the script-scoped rules; if any item fails, send the failures back to the script subagent; max 2 rounds, then ask the user. gated: show `script.md`, wait. | pass |
| 4 | images | Follow `sf-visual` for prompts; run `SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug>` then `sf_contact_sheet`. | all done |
| 5 | Gate 2 | Follow `sf-visual` self-review; redo flagged items; max 2 rounds, then ask the user. | pass |
| 6 | voice | Follow `sf-audio`; `sf_voice`. | all lines done |
| 7 | finish | `sf_align`, `sf_captions`, `sf_render`, `sf_qc`. Auto-fix only: re-run captions after re-wrapping, re-render after a regenerated asset. | QC ok, or remaining failures reviewed (see below) |
| 8 | learn | `sf_learn`. If `library_problems` is non-empty, fix the library file format and re-run. | ok |
| 9 | report | Video path, duration vs target, what was auto-fixed, open QC notes, and one line: "Feedback? `/story-feedback <slug> \"...\"`". | done |

Update `state.stage` as you pass each stage so a later `/story` resumes where it stopped.
Check services before stages 4 and 6 (`references/services.md`).

QC failures you judge acceptable after inspection (e.g. a natural 10 ms-over pause at a comma)
are reported as reviewed, not hidden.

## Objective defects → `library/checks.md`

When a gate or QC finds an objective defect (visible error, wrong count, text in image,
timing failure, length miss > 10 %), fix it, then add a check or bump the `hits` of the
existing one that covers it. Keep ≤ 30 per scope: when adding past the cap, delete the
entry with the fewest hits, oldest first. Checks are workflow knowledge, not taste.

## Taste → only `/story-feedback`

Never write `library/taste.md` except in the feedback flow (`references/feedback.md`).
Without user feedback, taste stays exactly as it is.

## Errors

- exit 2: read the summary's `needs_human`; fix what a skill can fix (prompt, text, casting), else ask the user.
- exit 3: provider quota/auth — stop and tell the user which provider and what to do.
- exit 1: read `projects/<slug>/logs/<script>.log`, report the bug; do not work around engine bugs silently.

## Subagents

Dispatch writing work (canon, script, rewrites) to subagents with: the brief, the matching
rules and checks verbatim, calibration numbers, exact file paths, and the exit criterion.
They never dispatch further agents. Run engine scripts yourself, one at a time (the project
lock allows one script per production).
```

- [ ] **Step 2: Write `.claude/skills/sf-director/references/services.md`**

```markdown
# Services

## VoiceStudio (voices + ASR) — required before `sf_voice`, `sf_align`

Health: `curl -s -m 3 http://localhost:3900/health` → `{"status":"ok",...}`.
If it fails, start it from the repo root and poll health every 5 s for up to 90 s:

    mkdir -p logs && (cd VoiceStudio && nohup uv run uvicorn main:app --app-dir backend --host 127.0.0.1 --port 3900 > ../logs/voicestudio.log 2>&1 &)

Models needed (install once via `POST /models/install {"repo_id": ...}`): `k2-fsa/OmniVoice`,
`mlx-community/whisper-large-v3-mlx`.

## Local image generation — used by `sf_image`

Always pass `SF_CONFIG=config/providers.local-image.yaml` (FLUX.2-klein-4B via mflux,
~20–30 s per image, ~13 GB RAM). Do not run it concurrently with another image job.
The default `config/providers.yaml` uses the `fake` provider (tests, smoke test).
```

- [ ] **Step 3: Write `.claude/skills/sf-director/references/feedback.md`**

```markdown
# Feedback flow (`/story-feedback <slug> "<feedback>"`)

The only path that writes `library/taste.md`.

1. Split the feedback into points. For each point decide:
   - **item fix** — names or clearly implies slides, lines, characters or locations (`S03`, "Bống's voice", "the ending");
   - **taste rule** — a preference that should hold beyond this video ("less text per slide", "warmer colors", "child voices younger");
   - usually both.
2. For each taste rule, append to `library/taste.md`:

       - T### [scope tags] <rule, imperative, one sentence>
         ← <slug> · <YYYY-MM-DD> · "<the user's words, verbatim>"

   Next id = highest existing T number + 1. Scope as narrow as the feedback implies
   (e.g. `vi · audio` for a Vietnamese voice remark; `global` only if the user says always/every).
   If it contradicts an existing rule of the same or broader scope, delete that rule and write
   "(replaces T###)" at the end of the new rule. If an existing rule already says the same, do nothing.
3. Apply item fixes through the owning skill: `sf-script` (text), `sf-visual` (prompts, seed), `sf-audio`
   (voice description, casting — re-cast with `--only <cast id>`). Then re-run only the affected
   stages and everything downstream: images → contact sheet; voice → align → captions → render → qc.
4. Run `sf_learn`; confirm `library_problems` is empty.
5. Report: rule ids written or replaced, items redone, new video path.
```

- [ ] **Step 4: Write the three commands**

`.claude/commands/story.md`:

```markdown
---
description: Make (or resume) a StoryForge video from an idea
argument-hint: "<idea>"
---

Use the `sf-director` skill. Idea: $ARGUMENTS

Derive a short kebab-case slug from the idea (Vietnamese diacritics removed). If
`projects/<slug>/story.json` exists, resume it at `state.stage`; otherwise run every stage
from brief to report.
```

`.claude/commands/story-feedback.md`:

```markdown
---
description: Give feedback on a StoryForge video; fixes it and teaches your taste
argument-hint: "<slug> \"<feedback>\""
---

Use the `sf-director` skill and follow `references/feedback.md` exactly. Arguments: $ARGUMENTS
```

`.claude/commands/story-redo.md`:

```markdown
---
description: Redo named items of a StoryForge production (no taste change)
argument-hint: "<slug> <id>[,<id>...]"
---

Use the `sf-director` skill. Arguments: $ARGUMENTS

Redo exactly these items (slides S##, lines L###, cast C## (voice re-cast), plates C##_face etc.,
locations LOC##): re-run the owning script with `--only <ids>` and then every downstream stage
(contact sheet; or align → captions → render → qc). Do not write `library/taste.md`.
```

- [ ] **Step 5: Add `/logs/` to `.gitignore`** (append the line `/logs/`).

- [ ] **Step 6: Verify**

Run: `grep -c "taste.md" .claude/skills/sf-director/SKILL.md .claude/skills/sf-director/references/feedback.md` → both ≥ 1.
Run: `head -4 .claude/commands/story.md` → frontmatter with `description`.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/sf-director .claude/commands .gitignore
git commit -m "$(cat <<'EOF'
Add sf-director skill and /story, /story-feedback, /story-redo commands

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: `sf-script`, `sf-visual`, `sf-audio` skills

**Files:**
- Create: `.claude/skills/sf-script/SKILL.md`, `.claude/skills/sf-script/references/rubric.md`, `.claude/skills/sf-script/references/speaking-rates.md`
- Create: `.claude/skills/sf-visual/SKILL.md`
- Create: `.claude/skills/sf-audio/SKILL.md`

**Interfaces:**
- Consumes: `sf-director` stage table (Task 4); `library/*` formats (Task 3); `schemas/story.schema.json`; templates `projects/smoke-test/story.json` (factual) and `projects/den-ong-sao/story.json` (fiction).
- Produces: the per-stage craft rules the director and subagents follow.

- [ ] **Step 1: Write `.claude/skills/sf-script/SKILL.md`**

```markdown
---
name: sf-script
description: Writes a StoryForge canon (Story Skills project) and adapts it into story.json lines and slides sized to the target duration. Use for stage 2 (canon + script) and Gate 1 rewrites of a StoryForge production.
---

# sf-script

## Inputs
Brief, matching taste rules and checks (verbatim), `library/calibration.json`, the slug.

## Canon (fiction/adaptation)
- Create `stories/<slug>/` with `story-init` conventions (read `.agents/skills/story-init/SKILL.md`).
  Use `scene-craft`, `chapter-writing`, `character-management` only as needed.
- One chapter `chapter-01`, scenes `scenes/chapter-01-scene-NN.md`.
- Check from the canon root: `node /Users/irondev/Desktop/Projects/chauvanhieu/yt/.agents/skills/story-maintenance/scripts/story.js validate` and `links` — clean.
- Factual content has no canon: `canon: null` and `research` notes + claims (see `projects/smoke-test/story.json`).

## Budget
`chars = (target_seconds − Σ pause_after_ms / 1000) × chars_per_s`, where chars are display
characters without spaces and `chars_per_s` is `calibration.speaking_rate[<lang>].chars_per_s`;
without calibration use `references/speaking-rates.md`. Aim within ±5 % of the budget.

## story.json
- Follow `schemas/story.schema.json`; copy structure from `projects/den-ong-sao/story.json` (fiction) or `projects/smoke-test/story.json` (factual). All asset entries start `pending`.
- Lines: written natively in `brief.language`; narration and dialogue on separate lines; short sentences; the first line is a hook within ~1.5 s; punctuation where the voice should pause; `pause_after_ms` 250–600 (longer at scene turns); only allowed tags (`[pause]`, `[pause 500ms]`, `[pause 1.5s]`, the OmniVoice non-verbal tags in `scripts/sflib/text.py`, `[[written|spoken]]`), prefer none.
- Slides: 9:16 → slides of 2–4 s, one drawable moment each; `source` = canon scene id; no two consecutive slides share scene, pose and shot; vary `motion` (static, push_in, pull_out, pan_left, pan_right); `text_placement` lower_third. Visual prompts are written by `sf-visual` rules.
- Write `projects/<slug>/script.md`: story summary, cast table, lines by slide.
- `sf_validate` must print `{"ok": true, "errors": []}`.

## Gate 1
Self-score with `references/rubric.md`; fix every failed item before handing back.
```

- [ ] **Step 2: Write `.claude/skills/sf-script/references/rubric.md`**

```markdown
# Gate 1 rubric (all must pass)

1. Hook: line 1 creates a question or stake within ~1.5 s of speech.
2. Arc: setup → turn → resolution is complete within the video; the ending lands on the last line.
3. Length: estimated duration (budget formula) within ±5 % of `target_seconds`.
4. Native language: reads as written by a native speaker; correct diacritics; no translationese.
5. TTS-ready: no stage directions in text, numbers/symbols written as spoken, only allowed tags.
6. Captions: no line needs more than ~3 caption cues (9:16: ≤ 18 chars per row, 2 rows).
7. Slides: every slide is one drawable moment; consecutive slides differ in scene, pose or shot.
8. Canon trace: every slide `source` exists; dialogue matches the canon.
9. Every matching taste rule (scope `script`, language, genre, global) is satisfied.
```

- [ ] **Step 3: Write `.claude/skills/sf-script/references/speaking-rates.md`**

```markdown
# Fallback speaking rates (display characters without spaces, per second of line audio)

Use only when `library/calibration.json` has no entry for the language. Measured values replace these after the first production.

| language | chars_per_s |
|---|---|
| vi | 13.0 |
| en | 14.0 |
| other | 12.0 |
```

- [ ] **Step 4: Write `.claude/skills/sf-visual/SKILL.md`**

```markdown
---
name: sf-visual
description: Writes StoryForge style bibles, character/location plate prompts and slide prompts, and self-reviews the contact sheet at Gate 2. Use for stage 4 (images) and 5 (Gate 2) of a StoryForge production.
---

# sf-visual

## Prompts
- Formula: style → subject/appearance → action → setting → shot → light → continuity → exclusions.
- The image model sees only the prompt plus the slide's character **face** plates and location plate
  (max 4). Repeat each visible character's key appearance words verbatim in every slide prompt.
- Face plates: "head-and-shoulders portrait, face fills the frame". Half: waist up. Full: head to toe, neutral background.
- State counts explicitly (people, moons, lanterns). End every prompt with: clean lower third, no text, no letters, no logos, no watermarks.
- Apply every matching image check in `library/checks.md` and every visual taste rule while writing, not only when reviewing.

## Generate
`SF_CONFIG=config/providers.local-image.yaml uv run scripts/sf_image.py projects/<slug>` then
`uv run scripts/sf_contact_sheet.py projects/<slug>`.

## Gate 2 self-review
1. Read `projects/<slug>/out/contact_sheet.png`; open any doubtful tile at full size (`images/<id>.png`, `plates/<id>.png`).
2. Flag objective defects: wrong count, duplicated objects, text/signatures, wrong character look vs its plates,
   missing `must_show`, present `must_not_show`, cluttered lower third, anatomy errors.
3. For each flagged item: edit the prompt (fix the cause), change `image.seed`, run `sf_image --only <ids>`,
   rebuild the contact sheet. Max 2 rounds, then ask the user with the sheet path.
4. Record each defect in `library/checks.md` (new check or `hits` bump) per sf-director rules.
```

- [ ] **Step 5: Write `.claude/skills/sf-audio/SKILL.md`**

```markdown
---
name: sf-audio
description: Casts StoryForge voices (library, design, clone) and handles voice generation, expressive controls and retakes. Use for stage 6 (voice) and voice-related redos or feedback in a StoryForge production.
---

# sf-audio

## Casting (per cast member, `voice` in story.json)
1. `source: library` + `library_ref` when `library/cast/<ref>/voice.json` exists (`{"profile_id", "instruct"}`) — reuse across videos.
2. `source: design` + `design_prompt`: comma-separated attribute words only, from:
   gender `male|female`; age `child|teenager|young adult|middle-aged|elderly`;
   pitch `very low pitch|low pitch|moderate pitch|high pitch|very high pitch`; optional accent
   (`american accent`, `british accent`, …; leave out for Vietnamese); optional `whisper`.
   Free-form emotion words are rejected.
3. `source: clone` + a user-supplied reference clip (strongest control over delivery).
Apply matching audio taste rules (e.g. how young child voices should sound).

## Expressive controls
Punctuation, `[pause]`, `[pause 500ms]`, `[pause 1.5s]`, `[laughter]`, `[sigh]`, `whisper: true`. Nothing else.

## Run
Check VoiceStudio (sf-director `references/services.md`), then `uv run scripts/sf_voice.py projects/<slug>`.
- `needs_human` for a line: read `audio.last_error` and `audio.qc`; fix text (punctuation, `[[written|spoken]]`
  for mispronounced words) and re-run with `--only <line id>`.
- Re-cast a voice: change `design_prompt`, run `sf_voice --only <cast id>`.

## Saving a recurring character
When the user asks to keep a voice for later videos, write `library/cast/<ref>/voice.json` with the
member's `profile_id` and `instruct`, and use `source: library` next time.
```

- [ ] **Step 6: Verify frontmatter**

Run: `for f in .claude/skills/sf-*/SKILL.md; do head -4 "$f" | grep -c "^name:\|^description:"; done` → each prints 2.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/sf-script .claude/skills/sf-visual .claude/skills/sf-audio
git commit -m "$(cat <<'EOF'
Add sf-script, sf-visual and sf-audio skills

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Seed calibration from real runs and update the base spec

**Files:**
- Create (generated): `library/calibration.json`, `library/runs/den-ong-sao.json`, `library/runs/smoke-test.json`
- Modify: `docs/superpowers/specs/2026-09-28-storyforge-design.md`
- Modify: `docs/superpowers/specs/2026-09-29-storyforge-director-and-evolution-design.md` (§7: `--check-library` is not a flag — validation runs on every `sf_learn` and exits 2 on problems; §6.3 seeding = mean of the first run's lines)

**Interfaces:**
- Consumes: `sf_learn` (Tasks 2–3); `projects/den-ong-sao` has voiced lines but no `logs/runs.jsonl` from before Task 1.

- [ ] **Step 1: Give the existing productions a measurement line**

The two productions were run before `runs.jsonl` existed. Re-run a cheap, cached step so each gets one log line (no regeneration happens: everything is cached):

Run: `uv run scripts/sf_render.py projects/den-ong-sao` → `"cached": 8`, `"rendered": []`.
Run: `uv run scripts/sf_validate.py projects/smoke-test`.
Check: `tail -1 projects/den-ong-sao/logs/runs.jsonl` shows `"script": "sf_render"`.

- [ ] **Step 2: Learn from them**

Run: `uv run scripts/sf_learn.py projects/den-ong-sao` → `"recorded": true`, `speaking_rate.vi` ≈ 13.
Run: `uv run scripts/sf_learn.py projects/smoke-test` → `"recorded": true` (smoke-test's committed story.json is pending, so it adds no speaking rate — expected).
Check: `library/calibration.json` has `speaking_rate.vi.lines == 16`.

- [ ] **Step 3: Update the base spec** (`docs/superpowers/specs/2026-09-28-storyforge-design.md`)

- §3 commands: replace `/story-new "<idea>"` with `/story "<idea>"` and add `/story-feedback <slug> "<feedback>"`.
- §4.2 gates: add one sentence — "With `review_mode: auto` (default), Gate 1 and Gate 2 are self-reviewed against the rubric, `library/taste.md` and `library/checks.md` (max 2 fix rounds, then the user is asked); see the Plan 2 spec."
- §6.1: skill list is now `sf-director`, `sf-script` (was `sf-video-script`, now also writes canon), `sf-visual`, `sf-audio`; `sf-finishing` folded into `sf-director`.
- File tree (§ repository layout): `library/learnings.md` → `library/taste.md`, `library/checks.md`, `library/calibration.json`, `library/runs/`.
- Replace "Appends one line per gate correction to `library/learnings.md`" with "User feedback becomes rules in `library/taste.md` (only via `/story-feedback`); objective defects become checks in `library/checks.md`."

- [ ] **Step 4: Update the Plan 2 spec** §6.3 ("seeded by the first run's mean" — already true) and §7: replace the `--check-library` bullet with "Every run validates `taste.md` and `checks.md` (`check_library`); problems are listed in `library_problems` and the script exits 2."

- [ ] **Step 5: Run the full suite and commit**

Run: `uv run pytest -q` → all pass.

```bash
git add library/calibration.json library/runs docs/superpowers/specs
git commit -m "$(cat <<'EOF'
Seed calibration from den-ong-sao and smoke-test; align specs with Plan 2

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Acceptance run (controller-driven)

**Files:** none new in the engine; creates `stories/<slug>/`, `projects/<slug>/` for a new short, and possibly `library/checks.md` / `library/taste.md` entries through the flows.

- [ ] **Step 1: `/story` in auto mode.** Follow `.claude/commands/story.md` → `sf-director` for a new idea (e.g. "Chú mèo mướp và cơn mưa đầu hạ — truyện thiếu nhi ấm áp"), with no user input. Expected: final `sf_qc` ok (or only reviewed notes); `library/runs/<slug>.json` last entry `actual_s` within ±10 % of `target_s` (60 s → 54–66 s); `predicted_s` present; `git diff library/taste.md` empty.
- [ ] **Step 2: `/story-feedback`.** Give one point, e.g. `"<slug>" "giọng người kể trầm và chậm hơn một chút"`. Expected: exactly one new `T###` rule in `library/taste.md` with the verbatim quote; only the narrator voice and downstream stages re-run; `git diff .claude/` empty.
- [ ] **Step 3: `/story` again without feedback** on a second small idea (or resume the same slug). Expected: `library/taste.md` byte-identical to after Step 2 (`git diff --stat library/taste.md` shows nothing new).
- [ ] **Step 4: Commit the productions and library updates.**

```bash
git add stories projects library
git commit -m "$(cat <<'EOF'
Acceptance run for Plan 2: auto production, feedback, no-feedback stability

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```
