# StoryForge Plan 1 — Production Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deterministic production engine: the `story.json` schema, shared helpers, and the eight `sf_*` scripts that turn a filled-in production into `out/final.mp4` with karaoke or plain captions.

**Architecture:** Each script is a small CLI (`uv run scripts/sf_x.py projects/<slug> [--only ids]`) that loads `story.json`, does one job, writes results back atomically, and prints one JSON summary line. Shared code lives in `scripts/sflib/`. Every script exposes `run(project_dir, only, ...) -> (summary, exit_code)` so tests call it directly with injected fakes (fake image provider, fake VoiceStudio client).

**Tech Stack:** Python ≥ 3.11 via `uv`, `httpx`, `jsonschema`, `Pillow`, `PyYAML`, `pytest`; system `ffmpeg`/`ffprobe` 8.x with libass.

**Spec:** `docs/superpowers/specs/2026-09-28-storyforge-design.md` (read §5 data contract and §8 scripts before starting).

## Global Constraints

- All code, comments, docs, and messages are in **English**.
- Python `>=3.11`; run everything through `uv run` from the workspace root `/Users/irondev/Desktop/Projects/chauvanhieu/yt`.
- Dependencies are exactly: `httpx`, `jsonschema`, `Pillow`, `PyYAML` (runtime) and `pytest` (dev). Add nothing else.
- Script stdout is **exactly one JSON line**; detailed logs go to `projects/<slug>/logs/`.
- Exit codes: `0` success, `1` bug, `2` needs human, `3` provider quota/auth.
- Provider error codes: `transient`, `content_blocked`, `quota`, `auth`, `invalid`.
- `story.json` writes are atomic (temp file + `os.replace`).
- Scripts own these fields and are the only writers: every asset's `path`, `input_hash`, `status`, `attempts`, `last_error`; `audio.duration_ms`, `audio.seed`, `audio.used_seed`, `audio.qc`, `audio.asr_words`; `words`, `words_hash`; `voice.profile_id`, `voice.instruct`; `output.*`.
- Video output: 1080×1920 (`9:16`) or 1920×1080 (`16:9`), 30 fps, H.264 yuv420p, AAC 48 kHz.
- Word times in `words` are **relative to the line start**.
- Plate aspects: face `1:1`, half `3:4`, full `9:16`; location plates use the production aspect.
- Allowed bracket tags in line `text`: `[pause]`, `[pause 500ms]`, `[pause 1.5s]`, the 13 OmniVoice non-verbal tags, and `[[written|spoken]]`.
- Commit messages end with the line `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## File Structure

```text
yt/
├── pyproject.toml                      # deps, pytest config (Task 1)
├── .python-version                     # 3.12 (Task 1)
├── .gitignore                          # + production media (Task 1)
├── config/
│   ├── providers.yaml                  # voice + image settings (Task 1)
│   └── caption-styles/
│       ├── karaoke-bold.yaml           # (Task 10)
│       └── subtitle-clean.yaml         # (Task 10)
├── schemas/story.schema.json           # production contract (Task 4)
├── scripts/
│   ├── sflib/
│   │   ├── __init__.py                 # (Task 1)
│   │   ├── project.py                  # IO, lock, hashing, CLI glue (Task 1)
│   │   ├── text.py                     # tags, display text, tokens (Task 2)
│   │   ├── timeline.py                 # ms/frame timeline (Task 3)
│   │   ├── media.py                    # ffmpeg/ffprobe helpers (Task 7)
│   │   └── voicestudio.py              # VoiceStudio HTTP client (Task 7)
│   ├── sf_validate.py                  # (Task 4)
│   ├── sf_image.py                     # (Task 5)
│   ├── sf_contact_sheet.py             # (Task 6)
│   ├── sf_voice.py                     # (Task 8)
│   ├── sf_align.py                     # (Task 9)
│   ├── sf_captions.py                  # (Task 10)
│   ├── sf_render.py                    # (Task 11)
│   └── sf_qc.py                        # (Task 12)
├── tests/
│   ├── fixtures.py                     # story builders, WAV helpers (Task 1, extended in 4 and 8)
│   ├── test_project.py  test_text.py  test_timeline.py  test_sf_validate.py
│   ├── test_sf_image.py  test_sf_contact_sheet.py  test_voicestudio.py  test_sf_voice.py
│   └── test_sf_align.py  test_sf_captions.py  test_sf_render.py  test_sf_qc.py
└── projects/smoke-test/story.json      # end-to-end smoke production (Task 13)
```

---

### Task 1: Scaffold and shared project IO

**Files:**
- Create: `pyproject.toml`, `.python-version`, `config/providers.yaml`, `scripts/sflib/__init__.py`, `scripts/sflib/project.py`, `tests/fixtures.py`, `tests/test_project.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces (in `sflib.project`):
  - `ROOT: Path` (workspace root), `EXIT_OK=0`, `EXIT_BUG=1`, `EXIT_HUMAN=2`, `EXIT_PROVIDER=3`
  - `class ProviderError(Exception)` with `.code: str`, `.message: str`
  - `class LockedError(Exception)`
  - `load_story(project_dir: Path) -> dict`, `save_story(project_dir: Path, story: dict) -> None`
  - `project_lock(project_dir: Path)` context manager
  - `load_config(path: Path | None = None) -> dict` (env `SF_CONFIG` overrides)
  - `input_hash(payload) -> str` (16 hex chars), `file_hash(path: Path) -> str`
  - `wanted(item_id: str, only: set[str] | None) -> bool`
  - `needs_work(entry: dict, new_hash: str, project_dir: Path) -> bool`
  - `log(project_dir: Path, name: str, message: str) -> None`
  - `main_wrapper(run, description: str) -> NoReturn`
- Produces (in `tests/fixtures.py`): `make_story(**overrides) -> dict`, `write_project(root: Path, story: dict) -> Path`, `asset(**extra) -> dict`

- [ ] **Step 1: Write `pyproject.toml`, `.python-version`, config, and ignore rules**

`pyproject.toml`:

```toml
[project]
name = "storyforge"
version = "0.1.0"
description = "StoryForge production engine scripts"
requires-python = ">=3.11"
dependencies = [
  "httpx>=0.27",
  "jsonschema>=4.22",
  "Pillow>=10.3",
  "PyYAML>=6.0",
]

[dependency-groups]
dev = ["pytest>=8.2"]

[tool.uv]
package = false

[tool.pytest.ini_options]
pythonpath = ["scripts", "tests"]
testpaths = ["tests"]
```

`.python-version`:

```text
3.12
```

`config/providers.yaml`:

```yaml
# StoryForge provider settings. Scripts read this file; set SF_CONFIG=<path> to use another.
voice:
  base_url: http://localhost:3900
  engine: null            # null = VoiceStudio's active engine (OmniVoice by default)
  qc:
    max_cer: 0.25         # transcribe-back character error rate allowed per line
    min_cps: 2            # speaking-rate band in characters per second (display text, no spaces)
    max_cps: 30
image:
  provider: fake          # fake | command
  # command: ["node", "/absolute/path/to/generate-image.js"]
  timeout_s: 1200
  max_refs: 4
```

Append to `.gitignore`:

```text
# production media and run state
projects/*/audio/
projects/*/images/
projects/*/plates/
projects/*/clips/
projects/*/out/
projects/*/logs/
projects/*/prompts/
projects/*/.sf.lock
projects/*/.story.*.tmp
.pytest_cache/
```

`scripts/sflib/__init__.py`: empty file.

- [ ] **Step 2: Write the failing tests**

`tests/fixtures.py`:

```python
"""Builders for test productions."""
from __future__ import annotations

import copy
import json
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
```

`tests/test_project.py`:

```python
import json

import pytest

from fixtures import make_story, write_project
from sflib.project import (
    LockedError, input_hash, load_config, load_story, needs_work, project_lock, save_story, wanted,
)


def test_save_and_load_roundtrip_leaves_no_temp_files(tmp_path):
    project = write_project(tmp_path, make_story())
    story = load_story(project)
    story["brief"]["idea"] = "Changed — with unicode ✓"
    save_story(project, story)
    assert load_story(project)["brief"]["idea"] == "Changed — with unicode ✓"
    assert [p.name for p in project.iterdir() if p.name.startswith(".story.")] == []


def test_lock_blocks_a_second_holder_and_is_released(tmp_path):
    with project_lock(tmp_path):
        with pytest.raises(LockedError):
            with project_lock(tmp_path):
                pass
    assert not (tmp_path / ".sf.lock").exists()


def test_input_hash_is_stable_and_key_order_independent():
    assert input_hash({"a": 1, "b": [1, 2]}) == input_hash({"b": [1, 2], "a": 1})
    assert input_hash({"a": 1}) != input_hash({"a": 2})
    assert len(input_hash({"a": 1})) == 16


def test_wanted_matches_exact_ids_and_prefixes():
    assert wanted("S01", None)
    assert wanted("S01", {"S01"})
    assert not wanted("S02", {"S01"})
    assert wanted("C01_face", {"C01"})
    assert wanted("C01_face", {"C01_face"})


def test_needs_work(tmp_path):
    (tmp_path / "a.png").write_bytes(b"x")
    done = {"status": "done", "input_hash": "h1", "path": "a.png"}
    assert not needs_work(done, "h1", tmp_path)
    assert needs_work(done, "h2", tmp_path)
    assert needs_work({**done, "path": "missing.png"}, "h1", tmp_path)
    assert needs_work({"status": "pending", "input_hash": None, "path": None}, "h1", tmp_path)
    assert not needs_work({"status": "needs_human", "input_hash": "h1", "path": None}, "h1", tmp_path)
    assert needs_work({"status": "needs_human", "input_hash": "h1", "path": None}, "h2", tmp_path)


def test_load_config_honors_env_override(tmp_path, monkeypatch):
    cfg = tmp_path / "p.yaml"
    cfg.write_text("image:\n  provider: fake\n", encoding="utf-8")
    monkeypatch.setenv("SF_CONFIG", str(cfg))
    assert load_config()["image"]["provider"] == "fake"
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/test_project.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sflib.project'`

- [ ] **Step 4: Implement `scripts/sflib/project.py`**

```python
"""Shared project IO for StoryForge scripts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, NoReturn

import yaml

ROOT = Path(__file__).resolve().parents[2]

EXIT_OK = 0
EXIT_BUG = 1
EXIT_HUMAN = 2
EXIT_PROVIDER = 3


class ProviderError(Exception):
    """A provider failure. code is one of: transient, content_blocked, quota, auth, invalid."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class LockedError(Exception):
    pass


def load_story(project_dir: Path) -> dict:
    return json.loads((project_dir / "story.json").read_text(encoding="utf-8"))


def save_story(project_dir: Path, story: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=project_dir, prefix=".story.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(story, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    os.replace(tmp, project_dir / "story.json")


@contextmanager
def project_lock(project_dir: Path) -> Iterator[None]:
    lock = project_dir / ".sf.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise LockedError(f"{lock} exists: another sf_ script is running, or delete this stale lock") from exc
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


def load_config(path: Path | None = None) -> dict:
    path = path or Path(os.environ.get("SF_CONFIG", ROOT / "config" / "providers.yaml"))
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def input_hash(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def file_hash(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def wanted(item_id: str, only: set[str] | None) -> bool:
    """True when --only is absent, names this id, or names its prefix (C01 matches C01_face)."""
    return only is None or item_id in only or item_id.split("_")[0] in only


def needs_work(entry: dict, new_hash: str, project_dir: Path) -> bool:
    """Decide whether an asset must be (re)generated when --only was not given."""
    if entry.get("input_hash") != new_hash:
        return True
    if entry.get("status") == "done":
        path = entry.get("path")
        return not (path and (project_dir / path).exists())
    return entry.get("status") in (None, "pending", "failed")


def log(project_dir: Path, name: str, message: str) -> None:
    logs = project_dir / "logs"
    logs.mkdir(exist_ok=True)
    with (logs / f"{name}.log").open("a", encoding="utf-8") as fh:
        fh.write(message.rstrip() + "\n")


def _parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("project_dir", type=Path, help="projects/<slug>")
    parser.add_argument("--only", default=None, help="comma-separated ids to (re)process, e.g. S07,L023,C01")
    args = parser.parse_args()
    args.only = {part for part in args.only.split(",") if part} if args.only else None
    args.project_dir = args.project_dir.resolve()
    return args


def _emit(summary: dict, code: int) -> NoReturn:
    print(json.dumps({"ok": code == EXIT_OK, **summary}, ensure_ascii=False))
    sys.exit(code)


def main_wrapper(run: Callable[..., tuple[dict, int]], description: str) -> NoReturn:
    args = _parse_args(description)
    try:
        with project_lock(args.project_dir):
            summary, code = run(args.project_dir, args.only)
    except LockedError as exc:
        _emit({"errors": [str(exc)]}, EXIT_HUMAN)
    _emit(summary, code)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run pytest tests/test_project.py -v`
Expected: 6 passed

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .python-version .gitignore config/providers.yaml scripts/sflib tests/fixtures.py tests/test_project.py uv.lock
git commit -m "$(cat <<'EOF'
Add StoryForge engine scaffold and shared project IO

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Script text handling

**Files:**
- Create: `scripts/sflib/text.py`, `tests/test_text.py`

**Interfaces:**
- Produces (in `sflib.text`):
  - `NONVERBAL_TAGS: tuple[str, ...]`
  - `invalid_tags(text: str) -> list[str]`: unsupported bracket spans
  - `display_text(text: str) -> str`: what captions show (tags removed, `[[written|spoken]]` → `written`)
  - `uses_clusters(language: str) -> bool`: `zh ja th lo km my` (base subtag)
  - `clusters(text: str) -> list[str]`: character clusters, marks and punctuation attached to the previous cluster
  - `tokens(text: str, language: str) -> list[str]`: caption tokens of `display_text(text)`
  - `norm(token: str) -> str`: NFC, casefold, punctuation removed (for matching)

- [ ] **Step 1: Write the failing tests**

`tests/test_text.py`:

```python
from sflib.text import clusters, display_text, invalid_tags, norm, tokens, uses_clusters


def test_invalid_tags_allows_supported_markup_only():
    ok = "Wait [pause] then [pause 500ms] and [pause 1.5s] [laughter] [sigh] [[gif|jiff]]."
    assert invalid_tags(ok) == []
    assert invalid_tags("She is [excited] now") == ["[excited]"]
    assert invalid_tags("Say [[Nuh-VAD-uh]]") == ["[[Nuh-VAD-uh]]"]


def test_display_text_strips_tags_and_keeps_written_half():
    assert display_text("Hello [laughter], [[gif|jiff]] fans [pause 300ms] !") == "Hello, gif fans!"
    assert display_text("No. [sigh] Not again.") == "No. Not again."


def test_tokens_for_spaced_language():
    assert tokens("Xin chào [sigh] các bạn.", "vi") == ["Xin", "chào", "các", "bạn."]


def test_tokens_for_cluster_language_attach_punctuation():
    assert uses_clusters("zh-Hans")
    assert not uses_clusters("en-US")
    assert tokens("你好，世界", "zh") == ["你", "好，", "世", "界"]


def test_clusters_keep_combining_marks_with_their_base():
    assert clusters("กิน") == ["กิ", "น"]


def test_norm_removes_punctuation_and_case():
    assert norm("Bạn.") == "bạn"
    assert norm("“Hello,”") == "hello"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_text.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sflib.text'`

- [ ] **Step 3: Implement `scripts/sflib/text.py`**

```python
"""Script text handling: expressive tags, display text, caption tokens."""
from __future__ import annotations

import re
import unicodedata

NONVERBAL_TAGS = (
    "laughter", "sigh", "confirmation-en", "question-en", "question-ah", "question-oh",
    "question-ei", "question-yi", "surprise-ah", "surprise-oh", "surprise-wa",
    "surprise-yo", "dissatisfaction-hnn",
)
_PAUSE = r"\[pause(?:\s+\d+(?:\.\d+)?(?:ms|s))?\]"
EXPRESSIVE_RE = re.compile(r"\[(?:" + "|".join(NONVERBAL_TAGS) + r")\]|" + _PAUSE)
OVERRIDE_RE = re.compile(r"\[\[([^\[\]|]+)\|([^\[\]]+)\]\]")
BRACKET_RE = re.compile(r"\[\[[^\]]*\]\]|\[[^\]]*\]")
CLUSTER_LANGS = {"zh", "ja", "th", "lo", "km", "my"}
_SPACE_BEFORE_PUNCT = re.compile(r"\s+([,.!?;:…。，！？、])")


def invalid_tags(text: str) -> list[str]:
    rest = EXPRESSIVE_RE.sub("", OVERRIDE_RE.sub("", text))
    return BRACKET_RE.findall(rest)


def display_text(text: str) -> str:
    shown = OVERRIDE_RE.sub(lambda m: m.group(1), text)
    shown = EXPRESSIVE_RE.sub(" ", shown)
    shown = re.sub(r"\s+", " ", shown).strip()
    return _SPACE_BEFORE_PUNCT.sub(r"\1", shown)


def uses_clusters(language: str) -> bool:
    return language.split("-")[0].lower() in CLUSTER_LANGS


def _is_punct(ch: str) -> bool:
    return unicodedata.category(ch).startswith("P")


def clusters(text: str) -> list[str]:
    out: list[str] = []
    for ch in unicodedata.normalize("NFC", text):
        if ch.isspace():
            continue
        if out and (unicodedata.category(ch).startswith("M") or _is_punct(ch)):
            out[-1] += ch
        else:
            out.append(ch)
    return out


def tokens(text: str, language: str) -> list[str]:
    shown = display_text(text)
    return clusters(shown) if uses_clusters(language) else shown.split()


def norm(token: str) -> str:
    folded = unicodedata.normalize("NFC", token).casefold()
    return "".join(ch for ch in folded if not _is_punct(ch))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_text.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/sflib/text.py tests/test_text.py
git commit -m "$(cat <<'EOF'
Add script text handling for tags, display text, and caption tokens

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Timeline

**Files:**
- Create: `scripts/sflib/timeline.py`, `tests/test_timeline.py`

**Interfaces:**
- Produces (in `sflib.timeline`):
  - `FPS = 30`
  - `ms_to_frame(ms: int) -> int`
  - `@dataclass SlideSpan(slide_id, start_ms, end_ms, start_frame, end_frame)` with property `frames`
  - `@dataclass Timeline(line_start_ms: dict[str,int], line_end_ms: dict[str,int], slides: list[SlideSpan], total_ms: int)` with property `total_frames`
  - `build_timeline(story: dict) -> Timeline` (raises `ValueError` when a line has no `audio.duration_ms`)

- [ ] **Step 1: Write the failing tests**

`tests/test_timeline.py`:

```python
import pytest

from fixtures import make_story
from sflib.timeline import build_timeline


def _with_durations(story, durations):
    for line, ms in zip(story["lines"], durations):
        line["audio"]["duration_ms"] = ms
    return story


def test_line_and_slide_spans_follow_measured_durations_and_pauses():
    tl = build_timeline(_with_durations(make_story(), [1000, 700, 1300]))
    assert tl.line_start_ms == {"L001": 0, "L002": 1250, "L003": 1950}
    assert tl.line_end_ms == {"L001": 1000, "L002": 1950, "L003": 3250}
    assert tl.total_ms == 3650
    s1, s2 = tl.slides
    assert (s1.slide_id, s1.start_ms, s1.end_ms) == ("S01", 0, 1950)
    assert (s2.slide_id, s2.start_ms, s2.end_ms) == ("S02", 1950, 3650)


def test_slide_frames_tile_the_whole_timeline_without_drift():
    tl = build_timeline(_with_durations(make_story(), [1000, 700, 1300]))
    assert tl.slides[0].end_frame == tl.slides[1].start_frame
    assert sum(s.frames for s in tl.slides) == tl.total_frames == 110


def test_missing_duration_raises():
    with pytest.raises(ValueError, match="L001"):
        build_timeline(make_story())
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_timeline.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sflib.timeline'`

- [ ] **Step 3: Implement `scripts/sflib/timeline.py`**

```python
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_timeline.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/sflib/timeline.py tests/test_timeline.py
git commit -m "$(cat <<'EOF'
Add drift-free ms/frame timeline from measured durations

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Schema and `sf_validate`

**Files:**
- Create: `schemas/story.schema.json`, `scripts/sf_validate.py`, `tests/test_sf_validate.py`

**Interfaces:**
- Consumes: `sflib.project` (`ROOT`, `EXIT_OK`, `EXIT_HUMAN`, `load_story`, `main_wrapper`), `sflib.text.invalid_tags`
- Produces: `sf_validate.run(project_dir: Path, only=None, root: Path = ROOT) -> tuple[dict, int]`; summary `{"errors": [str, ...]}`; exit `0` or `2`.

- [ ] **Step 1: Write the schema `schemas/story.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "StoryForge production (story.json)",
  "type": "object",
  "required": ["schema_version", "slug", "canon", "brief", "state", "style_bible", "cast", "locations", "slides", "lines", "research", "source_work", "output"],
  "properties": {
    "schema_version": {"const": "1.0"},
    "slug": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
    "canon": {
      "oneOf": [
        {"type": "null"},
        {
          "type": "object",
          "required": ["path", "chapters"],
          "properties": {
            "path": {"type": "string", "minLength": 1},
            "chapters": {"type": "array", "minItems": 1, "items": {"type": "string", "pattern": "^chapter-[0-9]{2,}$"}}
          }
        }
      ]
    },
    "brief": {
      "type": "object",
      "required": ["idea", "language", "aspect", "content_type", "genre", "target_seconds", "captions", "review_mode"],
      "properties": {
        "idea": {"type": "string", "minLength": 1},
        "language": {"type": "string", "pattern": "^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$"},
        "aspect": {"enum": ["9:16", "16:9"]},
        "content_type": {"enum": ["fiction", "factual", "adaptation"]},
        "genre": {"type": "string", "minLength": 1},
        "target_seconds": {"type": "integer", "minimum": 5},
        "captions": {
          "type": "object",
          "required": ["mode", "style"],
          "properties": {
            "mode": {"enum": ["karaoke", "plain", "none"]},
            "style": {"type": "string", "pattern": "^[a-z0-9-]+$"}
          }
        },
        "review_mode": {"const": "gated"}
      }
    },
    "state": {
      "type": "object",
      "required": ["stage", "gates"],
      "properties": {
        "stage": {"enum": ["brief", "idea", "canon", "research", "adapt", "checks", "gate1", "cast", "voice", "images", "gate2", "captions", "render", "qc", "done"]},
        "gates": {
          "type": "object",
          "required": ["script", "images"],
          "properties": {"script": {"$ref": "#/$defs/gate"}, "images": {"$ref": "#/$defs/gate"}}
        }
      }
    },
    "style_bible": {
      "type": "object",
      "required": ["medium", "palette", "lighting", "composition", "avoid"],
      "properties": {
        "medium": {"type": "string"},
        "palette": {"type": "array", "items": {"type": "string"}},
        "lighting": {"type": "string"},
        "composition": {"type": "string"},
        "avoid": {"type": "array", "items": {"type": "string"}}
      }
    },
    "cast": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/cast_member"}},
    "locations": {"type": "array", "items": {"$ref": "#/$defs/location"}},
    "slides": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/slide"}},
    "lines": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/line"}},
    "research": {"oneOf": [{"type": "null"}, {"$ref": "#/$defs/research"}]},
    "source_work": {"oneOf": [{"type": "null"}, {"$ref": "#/$defs/source_work"}]},
    "learnings_applied": {"type": "array", "items": {"type": "string"}},
    "output": {
      "type": "object",
      "required": ["video", "captions", "contact_sheet", "qc"],
      "properties": {
        "video": {"type": ["string", "null"]},
        "captions": {"type": ["string", "null"]},
        "contact_sheet": {"type": ["string", "null"]},
        "qc": {"type": ["string", "null"]}
      }
    }
  },
  "$defs": {
    "gate": {"type": "object", "required": ["approved_at"], "properties": {"approved_at": {"type": ["string", "null"]}}},
    "color": {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"},
    "asset": {
      "type": "object",
      "required": ["path", "input_hash", "status", "attempts"],
      "properties": {
        "path": {"type": ["string", "null"]},
        "input_hash": {"type": ["string", "null"]},
        "status": {"enum": ["pending", "done", "failed", "needs_human"]},
        "attempts": {"type": "integer", "minimum": 0},
        "last_error": {"type": ["string", "null"]}
      }
    },
    "plate": {
      "allOf": [
        {"$ref": "#/$defs/asset"},
        {"type": "object", "required": ["prompt"], "properties": {"prompt": {"type": "string", "minLength": 1}}}
      ]
    },
    "voice": {
      "type": "object",
      "required": ["source", "profile_id"],
      "properties": {
        "source": {"enum": ["library", "design", "clone"]},
        "profile_id": {"type": ["string", "null"]},
        "library_ref": {"type": "string"},
        "design_prompt": {"type": "string"},
        "instruct": {"type": "string"},
        "ref_audio": {"type": "string"},
        "ref_text": {"type": "string"}
      },
      "allOf": [
        {"if": {"properties": {"source": {"const": "library"}}}, "then": {"required": ["library_ref"]}},
        {"if": {"properties": {"source": {"const": "design"}}}, "then": {"required": ["design_prompt"]}},
        {"if": {"properties": {"source": {"const": "clone"}}}, "then": {"required": ["ref_audio"]}}
      ]
    },
    "cast_member": {
      "type": "object",
      "required": ["id", "canon_id", "name", "role", "voice", "caption_color"],
      "properties": {
        "id": {"type": "string", "pattern": "^(narrator|C[0-9]{2,})$"},
        "canon_id": {"type": ["string", "null"]},
        "name": {"type": "string", "minLength": 1},
        "role": {"enum": ["narrator", "protagonist", "antagonist", "deuteragonist", "supporting", "minor"]},
        "appearance": {"type": "string"},
        "pronunciation": {"type": "string"},
        "voice": {"$ref": "#/$defs/voice"},
        "caption_color": {"$ref": "#/$defs/color"},
        "plates": {
          "type": "object",
          "required": ["face", "half", "full"],
          "properties": {
            "face": {"$ref": "#/$defs/plate"},
            "half": {"$ref": "#/$defs/plate"},
            "full": {"$ref": "#/$defs/plate"}
          },
          "additionalProperties": false
        }
      }
    },
    "location": {
      "type": "object",
      "required": ["id", "canon_id", "name", "appearance", "plate"],
      "properties": {
        "id": {"type": "string", "pattern": "^LOC[0-9]{2,}$"},
        "canon_id": {"type": ["string", "null"]},
        "name": {"type": "string", "minLength": 1},
        "appearance": {"type": "string", "minLength": 1},
        "plate": {"$ref": "#/$defs/plate"}
      }
    },
    "slide": {
      "type": "object",
      "required": ["id", "source", "line_ids", "brief", "visual", "image"],
      "properties": {
        "id": {"type": "string", "pattern": "^S[0-9]{2,}$"},
        "source": {"type": ["string", "null"]},
        "line_ids": {"type": "array", "minItems": 1, "items": {"type": "string", "pattern": "^L[0-9]{3,}$"}},
        "brief": {
          "type": "object",
          "required": ["moment", "characters", "location", "must_show", "must_not_show", "continuity", "beat"],
          "properties": {
            "moment": {"type": "string", "minLength": 1},
            "characters": {"type": "array", "items": {"type": "string"}},
            "location": {"type": ["string", "null"]},
            "must_show": {"type": "array", "items": {"type": "string"}},
            "must_not_show": {"type": "array", "items": {"type": "string"}},
            "continuity": {"type": "array", "items": {"type": "string"}},
            "beat": {"enum": ["setup", "question", "reveal", "reversal", "emotional", "resolution"]}
          }
        },
        "visual": {
          "type": "object",
          "required": ["prompt", "shot", "motion", "text_placement"],
          "properties": {
            "prompt": {"type": "string", "minLength": 1},
            "shot": {"enum": ["extreme-close", "close-up", "medium", "wide", "extreme-wide"]},
            "motion": {"enum": ["static", "push_in", "pull_out", "pan_left", "pan_right"]},
            "text_placement": {"enum": ["lower_third", "center", "upper_third"]}
          }
        },
        "image": {
          "allOf": [
            {"$ref": "#/$defs/asset"},
            {"type": "object", "required": ["seed"], "properties": {"seed": {"type": ["integer", "null"]}}}
          ]
        }
      }
    },
    "word": {
      "type": "object",
      "required": ["text", "start_ms", "end_ms", "approx"],
      "properties": {
        "text": {"type": "string"},
        "start_ms": {"type": "integer", "minimum": 0},
        "end_ms": {"type": "integer", "minimum": 0},
        "approx": {"type": "boolean"}
      }
    },
    "line": {
      "type": "object",
      "required": ["id", "speaker", "text", "whisper", "pause_after_ms", "claim_ids", "audio", "words", "words_hash"],
      "properties": {
        "id": {"type": "string", "pattern": "^L[0-9]{3,}$"},
        "speaker": {"type": "string"},
        "text": {"type": "string", "minLength": 1},
        "whisper": {"type": "boolean"},
        "pause_after_ms": {"type": "integer", "minimum": 0, "maximum": 10000},
        "claim_ids": {"type": "array", "items": {"type": "string"}},
        "audio": {
          "allOf": [
            {"$ref": "#/$defs/asset"},
            {
              "type": "object",
              "required": ["duration_ms", "seed", "qc", "asr_words"],
              "properties": {
                "duration_ms": {"type": ["integer", "null"], "minimum": 1},
                "seed": {"type": ["integer", "null"]},
                "used_seed": {"type": ["integer", "null"]},
                "qc": {"type": ["object", "null"]},
                "asr_words": {"type": ["array", "null"]}
              }
            }
          ]
        },
        "words": {"type": "array", "items": {"$ref": "#/$defs/word"}},
        "words_hash": {"type": ["string", "null"]}
      }
    },
    "research": {
      "type": "object",
      "required": ["notes", "claims"],
      "properties": {
        "notes": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "title", "sources", "status"],
            "properties": {
              "id": {"type": "string", "pattern": "^R[0-9]{2,}$"},
              "title": {"type": "string"},
              "sources": {"type": "array", "items": {"type": "string"}},
              "status": {"enum": ["open", "verified", "disputed"]},
              "accuracy": {"enum": ["must-be-accurate", "blended", "invented"]},
              "confidence": {"enum": ["high", "medium", "low"]},
              "checked_on": {"type": ["string", "null"]},
              "risk": {"type": "array", "items": {"enum": ["legal", "medical", "weapons", "safety", "cultural", "defamation", "technical"]}}
            }
          }
        },
        "claims": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "text", "status", "note_ids"],
            "properties": {
              "id": {"type": "string", "pattern": "^CL[0-9]{2,}$"},
              "text": {"type": "string"},
              "status": {"enum": ["verified", "unverified", "interpretation"]},
              "note_ids": {"type": "array", "items": {"type": "string"}},
              "limitations": {"type": "string"}
            }
          }
        }
      }
    },
    "source_work": {
      "type": "object",
      "required": ["title", "author", "rights_basis", "translation_used"],
      "properties": {
        "title": {"type": "string"},
        "author": {"type": "string"},
        "rights_basis": {"type": "string"},
        "translation_used": {"type": ["string", "null"]}
      }
    }
  }
}
```

- [ ] **Step 2: Write the failing tests**

`tests/test_sf_validate.py`:

```python
from fixtures import make_story, write_project
import sf_validate


def _errors(tmp_path, story):
    summary, code = sf_validate.run(write_project(tmp_path, story), root=tmp_path)
    return summary["errors"], code


def test_fixture_story_is_valid(tmp_path):
    errors, code = _errors(tmp_path, make_story())
    assert errors == []
    assert code == 0


def test_schema_error_reports_path(tmp_path):
    story = make_story()
    story["slides"][0]["visual"]["motion"] = "spin"
    errors, code = _errors(tmp_path, story)
    assert code == 2
    assert any(e.startswith("slides/0/visual/motion:") for e in errors)


def test_unknown_speaker_and_character_and_location(tmp_path):
    story = make_story()
    story["lines"][0]["speaker"] = "C09"
    story["slides"][0]["brief"]["characters"] = ["C07"]
    story["slides"][1]["brief"]["location"] = "LOC09"
    errors, _ = _errors(tmp_path, story)
    assert "L001: speaker 'C09' is not in cast" in errors
    assert "S01: character 'C07' is not in cast" in errors
    assert "S02: location 'LOC09' is not in locations" in errors


def test_lines_must_follow_slide_order_exactly(tmp_path):
    story = make_story()
    story["slides"][0]["line_ids"] = ["L002", "L001"]
    errors, _ = _errors(tmp_path, story)
    assert any("line_ids" in e and "lines array order" in e for e in errors)


def test_unsupported_bracket_tag(tmp_path):
    story = make_story()
    story["lines"][1]["text"] = "Every [excited] night."
    errors, _ = _errors(tmp_path, story)
    assert any(e.startswith("L002: unsupported bracket tags") for e in errors)


def test_missing_canon_scene(tmp_path):
    story = make_story()
    project = write_project(tmp_path, story)
    (tmp_path / "stories/demo/scenes/chapter-01-scene-01.md").unlink()
    summary, _ = sf_validate.run(project, root=tmp_path)
    assert "S01: source scene 'chapter-01-scene-01' not found in canon" in summary["errors"]


def test_source_scene_outside_adapted_chapters(tmp_path):
    story = make_story()
    story["slides"][1]["source"] = "chapter-02-scene-01"
    errors, _ = _errors(tmp_path, story)
    assert "S02: source scene 'chapter-02-scene-01' is not in canon.chapters" in errors


def _factual(**research):
    story = make_story(canon=None)
    story["brief"]["content_type"] = "factual"
    for slide in story["slides"]:
        slide["source"] = None
    story["research"] = {
        "notes": [{"id": "R01", "title": "Tide tables", "sources": ["https://example.org/tides"], "status": "verified"}],
        "claims": [
            {"id": "CL01", "text": "High tide comes twice a day here.", "status": "verified", "note_ids": ["R01"]},
            {"id": "CL02", "text": "The light was built in 1851.", "status": "unverified", "note_ids": []},
        ],
        **research,
    }
    return story


def test_factual_claims_must_resolve_and_be_resolved(tmp_path):
    story = _factual()
    story["lines"][0]["claim_ids"] = ["CL01"]
    assert _errors(tmp_path, story)[0] == []
    story["lines"][1]["claim_ids"] = ["CL02", "CL09"]
    errors, code = _errors(tmp_path / "b", story)
    assert code == 2
    assert "L002: claim 'CL09' is not in research.claims" in errors
    assert "L002: claim 'CL02' is unverified; verify it or remove it before Gate 1" in errors


def test_factual_requires_research(tmp_path):
    story = _factual()
    story["research"] = None
    errors, _ = _errors(tmp_path, story)
    assert "factual content requires research" in errors


def test_adaptation_requires_rights_basis(tmp_path):
    story = make_story()
    story["brief"]["content_type"] = "adaptation"
    story["source_work"] = {"title": "The Snow Queen", "author": "H. C. Andersen", "rights_basis": "", "translation_used": None}
    errors, _ = _errors(tmp_path, story)
    assert "adaptation requires source_work.rights_basis" in errors
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/test_sf_validate.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sf_validate'`

- [ ] **Step 4: Implement `scripts/sf_validate.py`**

```python
#!/usr/bin/env python3
"""Validate a production's story.json: JSON schema, then cross references."""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from sflib.project import EXIT_HUMAN, EXIT_OK, ROOT, load_story, main_wrapper
from sflib.text import invalid_tags

SCHEMA_PATH = ROOT / "schemas" / "story.schema.json"


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


def reference_errors(story: dict, root: Path) -> list[str]:
    cast_ids = [c["id"] for c in story["cast"]]
    location_ids = [loc["id"] for loc in story["locations"]]
    line_ids = [line["id"] for line in story["lines"]]
    slide_ids = [slide["id"] for slide in story["slides"]]
    errors = (
        _duplicates("cast", cast_ids) + _duplicates("location", location_ids)
        + _duplicates("line", line_ids) + _duplicates("slide", slide_ids)
    )
    if [lid for slide in story["slides"] for lid in slide["line_ids"]] != line_ids:
        errors.append("slides' line_ids, concatenated in slide order, must equal the lines array order exactly "
                      "(each line belongs to exactly one slide)")
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
    return errors


def run(project_dir: Path, only: set[str] | None = None, root: Path = ROOT) -> tuple[dict, int]:
    story = load_story(project_dir)
    errors = schema_errors(story) or reference_errors(story, root)
    return {"errors": errors}, EXIT_OK if not errors else EXIT_HUMAN


if __name__ == "__main__":
    main_wrapper(run, __doc__)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run pytest tests/test_sf_validate.py -v`
Expected: 10 passed

- [ ] **Step 6: Commit**

```bash
git add schemas/story.schema.json scripts/sf_validate.py tests/test_sf_validate.py
git commit -m "$(cat <<'EOF'
Add story.json schema and sf_validate cross-reference checks

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: `sf_image` with fake and command providers

**Files:**
- Create: `scripts/sf_image.py`, `tests/test_sf_image.py`

**Interfaces:**
- Consumes: `sflib.project` (`EXIT_*`, `ProviderError`, `file_hash`, `input_hash`, `load_config`, `load_story`, `save_story`, `log`, `main_wrapper`, `needs_work`, `wanted`)
- Produces:
  - `sf_image.SIZES: dict[str, tuple[int, int]]` = `{"1:1": (1024, 1024), "3:4": (768, 1024), "9:16": (1080, 1920), "16:9": (1920, 1080)}`
  - `sf_image.PLATE_ASPECT = {"face": "1:1", "half": "3:4", "full": "9:16"}`
  - `sf_image.run(project_dir, only=None, config=None, sleep=time.sleep) -> tuple[dict, int]`; summary `{"done": [ids], "skipped": int, "needs_human": [ids], "blocked": [str], "errors": [str]}`
  - Item ids: `C01_face`, `C01_half`, `C01_full`, `LOC01`, `S01`. Files: `plates/<id>.png`, `images/<slide>.png`. Prompts for the command provider: `prompts/<id>.txt`.

- [ ] **Step 1: Write the failing tests**

`tests/test_sf_image.py`:

```python
import json
import sys
import textwrap

from PIL import Image

from fixtures import make_story, write_project
import sf_image
from sflib.project import load_story, save_story

FAKE = {"image": {"provider": "fake", "max_refs": 4}}


def _command_config(tmp_path, fail_when: str, error: str) -> dict:
    script = tmp_path / "provider.py"
    script.write_text(textwrap.dedent(f"""
        import json, sys
        from PIL import Image
        args = sys.argv[1:]
        out = args[args.index("--out") + 1]
        aspect = args[args.index("--aspect") + 1]
        if {fail_when!r} in out:
            print(json.dumps({{"error": {error!r}, "message": "refused"}}), file=sys.stderr)
            sys.exit(1)
        sizes = {{"1:1": (64, 64), "3:4": (48, 64), "9:16": (36, 64), "16:9": (64, 36)}}
        Image.new("RGB", sizes[aspect], "gray").save(out)
    """), encoding="utf-8")
    return {"image": {"provider": "command", "command": [sys.executable, str(script)], "timeout_s": 30, "max_refs": 4}}


def test_generates_plates_then_slides_with_correct_sizes(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_image.run(project, config=FAKE)
    assert code == 0
    assert summary["done"] == ["C01_face", "C01_half", "C01_full", "LOC01", "S01", "S02"]
    story = load_story(project)
    face = story["cast"][1]["plates"]["face"]
    assert face["status"] == "done" and face["path"] == "plates/C01_face.png"
    assert Image.open(project / "plates/C01_face.png").size == (1024, 1024)
    assert Image.open(project / "plates/C01_half.png").size == (768, 1024)
    assert Image.open(project / "images/S01.png").size == (1080, 1920)
    assert story["slides"][0]["image"]["attempts"] == 1


def test_second_run_skips_and_prompt_change_regenerates_only_that_slide(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_image.run(project, config=FAKE)
    summary, _ = sf_image.run(project, config=FAKE)
    assert summary["done"] == [] and summary["skipped"] == 6
    story = load_story(project)
    story["slides"][1]["visual"]["prompt"] = "A second light, closer now"
    save_story(project, story)
    summary, _ = sf_image.run(project, config=FAKE)
    assert summary["done"] == ["S02"]


def test_only_forces_regeneration_by_prefix(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_image.run(project, config=FAKE)
    summary, _ = sf_image.run(project, only={"C01"}, config=FAKE)
    assert summary["done"] == ["C01_face", "C01_half", "C01_full"]


def test_content_blocked_face_plate_blocks_its_slides(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_image.run(project, config=_command_config(tmp_path, "_face", "content_blocked"), sleep=lambda s: None)
    assert code == 2
    assert summary["needs_human"] == ["C01_face"]
    assert summary["blocked"] == ["S01 waits for C01_face", "S02 waits for C01_face"]
    face = load_story(project)["cast"][1]["plates"]["face"]
    assert face["status"] == "needs_human" and face["last_error"] == "content_blocked: refused"
    assert (project / "prompts/C01_face.txt").read_text(encoding="utf-8") == "Portrait of Mara, face plate"


def test_quota_stops_the_run_with_exit_3_and_keeps_progress(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_image.run(project, config=_command_config(tmp_path, "LOC01", "quota"), sleep=lambda s: None)
    assert code == 3
    assert summary["errors"] == ["quota: refused"]
    story = load_story(project)
    assert story["cast"][1]["plates"]["full"]["status"] == "done"
    assert story["slides"][0]["image"]["status"] == "pending"


def test_wrong_aspect_marks_needs_human(tmp_path):
    project = write_project(tmp_path, make_story())
    config = _command_config(tmp_path, "never", "invalid")
    script = tmp_path / "provider.py"
    script.write_text(script.read_text().replace('"9:16": (36, 64)', '"9:16": (64, 64)'), encoding="utf-8")
    summary, code = sf_image.run(project, config=config)
    assert code == 2
    assert "LOC01" in summary["needs_human"]
    assert "expected aspect 9:16" in load_story(project)["locations"][0]["plate"]["last_error"]
    assert summary["blocked"] == ["S01 waits for LOC01", "S02 waits for LOC01"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_sf_image.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sf_image'`

- [ ] **Step 3: Implement `scripts/sf_image.py`**

```python
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
    for character in slide["brief"]["characters"]:
        plates = cast[character].get("plates")
        if plates:
            refs.append(plates["face"]["path"])
    if slide["brief"]["location"]:
        refs.append(locations[slide["brief"]["location"]]["plate"]["path"])
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
        try:
            _generate_with_retries(provider, prompt, aspect, [project_dir / ref for ref in refs], seed, out, sleep)
            check_image(out, aspect)
        except ProviderError as exc:
            if exc.code in ("quota", "auth", "invalid"):
                raise
            entry.update(status="needs_human", input_hash=new_hash, last_error=f"{exc.code}: {exc.message}")
            summary["needs_human"].append(item)
        except QualityError as exc:
            entry.update(status="needs_human", input_hash=new_hash, last_error=str(exc))
            summary["needs_human"].append(item)
        else:
            entry.update(status="done", path=rel_path, input_hash=new_hash, last_error=None)
            summary["done"].append(item)
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_sf_image.py -v`
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/sf_image.py tests/test_sf_image.py
git commit -m "$(cat <<'EOF'
Add sf_image with fake and command providers, plates before slides

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: `sf_contact_sheet`

**Files:**
- Create: `scripts/sf_contact_sheet.py`, `tests/test_sf_contact_sheet.py`

**Interfaces:**
- Consumes: `sflib.project`, `sflib.text.display_text`, `sf_image.run` (tests only)
- Produces: `sf_contact_sheet.run(project_dir, only=None) -> tuple[dict, int]`; writes `out/contact_sheet.png`; sets `output.contact_sheet`; summary `{"tiles": int, "missing": [ids]}`; exit `2` when any tile is missing. Layout constants: `CELL = {"9:16": (270, 480), "16:9": (480, 270)}`, `COLS = {"9:16": 6, "16:9": 4}`, `LABEL_H = 56`, `PAD = 12`.

- [ ] **Step 1: Write the failing tests**

`tests/test_sf_contact_sheet.py`:

```python
from PIL import Image

from fixtures import make_story, write_project
import sf_contact_sheet
import sf_image
from sflib.project import load_story


def test_contact_sheet_has_every_plate_and_slide(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_image.run(project, config={"image": {"provider": "fake", "max_refs": 4}})
    summary, code = sf_contact_sheet.run(project)
    assert code == 0
    assert summary == {"tiles": 6, "missing": []}
    sheet = Image.open(project / "out/contact_sheet.png")
    # 6 tiles in one row of 6 columns: width = 6*270 + 7*12, height = 480 + 56 + 2*12
    assert sheet.size == (6 * 270 + 7 * 12, 480 + 56 + 2 * 12)
    assert load_story(project)["output"]["contact_sheet"] == "out/contact_sheet.png"


def test_missing_images_are_reported(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_contact_sheet.run(project)
    assert code == 2
    assert summary["missing"] == ["C01_face", "C01_half", "C01_full", "LOC01", "S01", "S02"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_sf_contact_sheet.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sf_contact_sheet'`

- [ ] **Step 3: Implement `scripts/sf_contact_sheet.py`**

```python
#!/usr/bin/env python3
"""Build out/contact_sheet.png: every plate and slide with its id, for Gate 2 review."""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from sflib.project import EXIT_HUMAN, EXIT_OK, load_story, main_wrapper, save_story
from sflib.text import display_text

CELL = {"9:16": (270, 480), "16:9": (480, 270)}
COLS = {"9:16": 6, "16:9": 4}
LABEL_H = 56
PAD = 12


def _tiles(story: dict) -> list[tuple[str, str, str | None]]:
    """(id, caption, image path or None) for plates, then slides."""
    tiles = []
    for member in story["cast"]:
        for kind, plate in (member.get("plates") or {}).items():
            tiles.append((f"{member['id']}_{kind}", member["name"], plate["path"] if plate["status"] == "done" else None))
    for location in story["locations"]:
        plate = location["plate"]
        tiles.append((location["id"], location["name"], plate["path"] if plate["status"] == "done" else None))
    lines = {line["id"]: line for line in story["lines"]}
    for slide in story["slides"]:
        first = display_text(lines[slide["line_ids"][0]]["text"])
        image = slide["image"]
        tiles.append((slide["id"], first[:40], image["path"] if image["status"] == "done" else None))
    return tiles


def run(project_dir: Path, only: set[str] | None = None) -> tuple[dict, int]:
    story = load_story(project_dir)
    aspect = story["brief"]["aspect"]
    cell_w, cell_h = CELL[aspect]
    tiles = _tiles(story)
    cols = min(COLS[aspect], len(tiles))
    rows = math.ceil(len(tiles) / cols)
    sheet = Image.new("RGB", (cols * cell_w + (cols + 1) * PAD, rows * (cell_h + LABEL_H) + (rows + 1) * PAD), "#1e1e1e")
    draw = ImageDraw.Draw(sheet)
    id_font = ImageFont.load_default(size=20)
    caption_font = ImageFont.load_default(size=14)
    missing = []
    for index, (item, caption, rel_path) in enumerate(tiles):
        x = PAD + (index % cols) * (cell_w + PAD)
        y = PAD + (index // cols) * (cell_h + LABEL_H + PAD)
        path = project_dir / rel_path if rel_path else None
        if path and path.exists():
            with Image.open(path) as image:
                thumb = ImageOps.contain(image.convert("RGB"), (cell_w, cell_h))
            sheet.paste(thumb, (x + (cell_w - thumb.width) // 2, y + (cell_h - thumb.height) // 2))
        else:
            missing.append(item)
            draw.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], fill="#555555")
            draw.text((x + cell_w // 2, y + cell_h // 2), "MISSING", fill="white", anchor="mm", font=id_font)
        draw.text((x, y + cell_h + 6), item, fill="white", font=id_font)
        draw.text((x, y + cell_h + 32), caption, fill="#bbbbbb", font=caption_font)
    out = project_dir / "out" / "contact_sheet.png"
    out.parent.mkdir(exist_ok=True)
    sheet.save(out)
    story["output"]["contact_sheet"] = "out/contact_sheet.png"
    save_story(project_dir, story)
    return {"tiles": len(tiles), "missing": missing}, EXIT_HUMAN if missing else EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_sf_contact_sheet.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/sf_contact_sheet.py tests/test_sf_contact_sheet.py
git commit -m "$(cat <<'EOF'
Add sf_contact_sheet for Gate 2 image review

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Media helpers and VoiceStudio client

**Files:**
- Create: `scripts/sflib/media.py`, `scripts/sflib/voicestudio.py`, `tests/test_voicestudio.py`
- Modify: `tests/fixtures.py` (add WAV helpers)

**Interfaces:**
- Produces (in `sflib.media`):
  - `probe_duration_ms(path: Path) -> int`
  - `probe_video(path: Path) -> dict` → `{"width": int, "height": int, "frames": int}`
  - `probe_audio_ms(path: Path) -> int`
  - `has_filter(name: str) -> bool`
  - `run_ffmpeg(args: list[str], cwd: Path | None = None) -> None` (raises `RuntimeError` with stderr)
  - `decode_pcm(path: Path, rate: int = 48000) -> bytes` (mono s16le)
  - `silences(path: Path, noise_db: int = -45, min_s: float = 0.3) -> list[float]` (durations in seconds)
- Produces (in `sflib.voicestudio`): `class VoiceStudio(base_url, *, transport=None, timeout_s=1900.0)` with
  - `health() -> None` (unreachable → `ProviderError("auth")`)
  - `describe(description: str) -> dict` (`{"attrs", "instruct", ...}`)
  - `create_design_profile(name, attrs: dict, instruct: str, language: str) -> str`
  - `create_clone_profile(name, ref_audio: Path, ref_text: str, language: str) -> str`
  - `generate(*, text, language, profile_id, seed, engine=None, instruct=None) -> tuple[bytes, dict]` (meta keys `seed`, `duration_s`, `dropped_chunks`)
  - `transcribe_words(wav: Path, language: str) -> list[dict]` (`{"text", "start", "end"}`, seconds or `None`)
- Produces (in `tests/fixtures.py`): `sine_wav_bytes(ms: int, rate: int = 24000) -> bytes`

- [ ] **Step 1: Add the WAV helper to `tests/fixtures.py`**

Add at the top with the other imports:

```python
import io
import math
import struct
import wave
```

Add at the end of the file:

```python
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
```

- [ ] **Step 2: Write the failing tests**

`tests/test_voicestudio.py`:

```python
import json

import httpx
import pytest

from fixtures import sine_wav_bytes
from sflib.media import probe_duration_ms
from sflib.project import ProviderError
from sflib.voicestudio import VoiceStudio


def _client(handler) -> VoiceStudio:
    return VoiceStudio("http://vs.local", transport=httpx.MockTransport(handler))


def test_design_profile_flow_sends_form_fields():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/design/describe":
            assert json.loads(request.content) == {"description": "female, elderly"}
            return httpx.Response(200, json={"attrs": {"Gender": "female", "Age": "elderly"}, "instruct": "female, elderly"})
        if request.url.path == "/profiles":
            seen["body"] = request.content.decode()
            return httpx.Response(200, json={"id": "ab12cd34", "name": "x"})
        return httpx.Response(404)

    vs = _client(handler)
    parsed = vs.describe("female, elderly")
    profile = vs.create_design_profile("demo-C01", parsed["attrs"], parsed["instruct"], "en")
    assert profile == "ab12cd34"
    assert "kind=design" in seen["body"] and "vd_states=" in seen["body"] and "language=en" in seen["body"]


def test_generate_returns_wav_and_header_metadata(tmp_path):
    wav = sine_wav_bytes(500)

    def handler(request: httpx.Request) -> httpx.Response:
        body = request.content.decode()
        assert "profile_id=p1" in body and "seed=7" in body and "instruct=whisper" in body
        return httpx.Response(200, content=wav, headers={"X-Seed": "7", "X-Audio-Duration": "0.5"})

    data, meta = _client(handler).generate(text="Hi", language="en", profile_id="p1", seed=7, instruct="whisper")
    path = tmp_path / "a.wav"
    path.write_bytes(data)
    assert meta == {"seed": "7", "duration_s": "0.5", "dropped_chunks": None}
    assert probe_duration_ms(path) == 500


@pytest.mark.parametrize("status,headers,code", [
    (409, {}, "auth"),
    (503, {"X-OmniVoice-Retryable": "true"}, "transient"),
    (500, {}, "transient"),
    (400, {}, "invalid"),
])
def test_error_mapping(status, headers, code):
    vs = _client(lambda request: httpx.Response(status, json={"detail": "boom"}, headers=headers))
    with pytest.raises(ProviderError) as info:
        vs.generate(text="Hi", language="en", profile_id="p1", seed=1)
    assert info.value.code == code
    assert "boom" in info.value.message


def test_health_unreachable_is_auth():
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    with pytest.raises(ProviderError) as info:
        _client(handler).health()
    assert info.value.code == "auth"
    assert "open the VoiceStudio app" in info.value.message


def test_transcribe_words_flattens_segment_words(tmp_path):
    wav = tmp_path / "a.wav"
    wav.write_bytes(sine_wav_bytes(300))

    def handler(request: httpx.Request) -> httpx.Response:
        assert b'name="mode"' in request.content and b"accurate" in request.content
        return httpx.Response(200, json={"segments": [
            {"text": "Every night", "words": [{"word": " Every", "start": 0.0, "end": 0.3}, {"word": "night", "start": 0.3, "end": 0.6}]},
            {"text": "for 11", "words": [{"word": "for", "start": 0.6, "end": 0.8}, {"word": "11"}]},
        ]})

    words = _client(handler).transcribe_words(wav, "en")
    assert words == [
        {"text": "Every", "start": 0.0, "end": 0.3},
        {"text": "night", "start": 0.3, "end": 0.6},
        {"text": "for", "start": 0.6, "end": 0.8},
        {"text": "11", "start": None, "end": None},
    ]
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/test_voicestudio.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sflib.media'`

- [ ] **Step 4: Implement `scripts/sflib/media.py`**

```python
"""Thin wrappers around ffmpeg and ffprobe."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


def _probe(args: list[str]) -> dict:
    proc = subprocess.run(["ffprobe", "-v", "error", *args, "-of", "json"], capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def probe_duration_ms(path: Path) -> int:
    data = _probe(["-show_entries", "format=duration", str(path)])
    return round(float(data["format"]["duration"]) * 1000)


def probe_video(path: Path) -> dict:
    data = _probe(["-count_frames", "-select_streams", "v:0", "-show_entries", "stream=width,height,nb_read_frames", str(path)])
    stream = data["streams"][0]
    return {"width": int(stream["width"]), "height": int(stream["height"]), "frames": int(stream["nb_read_frames"])}


def probe_audio_ms(path: Path) -> int:
    data = _probe(["-select_streams", "a:0", "-show_entries", "stream=duration", str(path)])
    return round(float(data["streams"][0]["duration"]) * 1000)


def has_filter(name: str) -> bool:
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True, check=True)
    return any(line.split()[1:2] == [name] for line in proc.stdout.splitlines() if line.strip())


def run_ffmpeg(args: list[str], cwd: Path | None = None) -> None:
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args],
                          capture_output=True, text=True, cwd=cwd)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {' '.join(args)}\n{proc.stderr.strip()}")


def decode_pcm(path: Path, rate: int = 48000) -> bytes:
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path),
                           "-f", "s16le", "-ac", "1", "-ar", str(rate), "-"], capture_output=True, check=True)
    return proc.stdout


def silences(path: Path, noise_db: int = -45, min_s: float = 0.3) -> list[float]:
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af",
                           f"silencedetect=noise={noise_db}dB:d={min_s}", "-f", "null", "-"],
                          capture_output=True, text=True)
    return [float(v) for v in re.findall(r"silence_duration: ([0-9.]+)", proc.stderr)]
```

- [ ] **Step 5: Implement `scripts/sflib/voicestudio.py`**

```python
"""Minimal client for the VoiceStudio local API (docs: VoiceStudio/docs, backend/api/routers)."""
from __future__ import annotations

import json
from pathlib import Path

import httpx

from sflib.project import ProviderError


def _detail(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text[:300]
    detail = body.get("detail", body) if isinstance(body, dict) else body
    return detail[:300] if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)[:300]


class VoiceStudio:
    def __init__(self, base_url: str, *, transport: httpx.BaseTransport | None = None, timeout_s: float = 1900.0):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, transport=transport,
                                   timeout=httpx.Timeout(timeout_s, connect=10.0))

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            response = self.client.request(method, url, **kwargs)
        except httpx.TransportError as exc:
            raise ProviderError("transient", f"VoiceStudio {method} {url}: {exc}") from exc
        if response.status_code < 400:
            return response
        detail = _detail(response)
        if response.status_code == 409:
            raise ProviderError("auth", f"VoiceStudio setup needed: {detail}")
        if response.status_code >= 500 or response.status_code == 429 \
                or response.headers.get("X-OmniVoice-Retryable") == "true":
            raise ProviderError("transient", detail)
        raise ProviderError("invalid", f"{response.status_code}: {detail}")

    def health(self) -> None:
        try:
            response = self.client.get("/health")
        except httpx.TransportError as exc:
            raise ProviderError("auth", f"VoiceStudio is not reachable at {self.base_url}; "
                                        f"open the VoiceStudio app first ({exc})") from exc
        if response.status_code >= 400:
            raise ProviderError("auth", f"VoiceStudio /health returned {response.status_code}")

    def describe(self, description: str) -> dict:
        return self._request("POST", "/design/describe", json={"description": description}).json()

    def create_design_profile(self, name: str, attrs: dict, instruct: str, language: str) -> str:
        response = self._request("POST", "/profiles", data={
            "name": name, "kind": "design", "vd_states": json.dumps(attrs), "instruct": instruct, "language": language,
        })
        return response.json()["id"]

    def create_clone_profile(self, name: str, ref_audio: Path, ref_text: str, language: str) -> str:
        with ref_audio.open("rb") as fh:
            response = self._request("POST", "/profiles", data={
                "name": name, "kind": "clone", "ref_text": ref_text, "language": language,
            }, files={"ref_audio": (ref_audio.name, fh, "audio/wav")})
        return response.json()["id"]

    def generate(self, *, text: str, language: str, profile_id: str, seed: int,
                 engine: str | None = None, instruct: str | None = None) -> tuple[bytes, dict]:
        data = {"text": text, "language": language, "profile_id": profile_id, "seed": str(seed)}
        if engine:
            data["engine"] = engine
        if instruct:
            data["instruct"] = instruct
        response = self._request("POST", "/generate", data=data)
        meta = {
            "seed": response.headers.get("X-Seed"),
            "duration_s": response.headers.get("X-Audio-Duration"),
            "dropped_chunks": response.headers.get("X-OmniVoice-Dropped-Chunks"),
        }
        return response.content, meta

    def transcribe_words(self, wav: Path, language: str) -> list[dict]:
        with wav.open("rb") as fh:
            response = self._request("POST", "/transcribe", data={"language": language, "mode": "accurate"},
                                     files={"audio": (wav.name, fh, "audio/wav")})
        words = []
        for segment in response.json().get("segments", []):
            for word in segment.get("words") or []:
                text = (word.get("word") or word.get("text") or "").strip()
                if text:
                    words.append({"text": text, "start": word.get("start"), "end": word.get("end")})
        return words
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `uv run pytest tests/test_voicestudio.py -v`
Expected: 8 passed

- [ ] **Step 7: Commit**

```bash
git add scripts/sflib/media.py scripts/sflib/voicestudio.py tests/test_voicestudio.py tests/fixtures.py
git commit -m "$(cat <<'EOF'
Add ffmpeg helpers and VoiceStudio client with error mapping

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: `sf_voice`

**Files:**
- Create: `scripts/sf_voice.py`, `tests/test_sf_voice.py`

**Interfaces:**
- Consumes: `sflib.project`, `sflib.media.probe_duration_ms`, `sflib.text.display_text`, `sflib.text.norm`, `sflib.voicestudio.VoiceStudio`
- Produces:
  - `sf_voice.cer(reference: str, hypothesis: str) -> float`
  - `sf_voice.default_seed(slug: str, line_id: str) -> int`
  - `sf_voice.RETAKE_SEED_STEP = 7919`, `sf_voice.MAX_RETAKES = 2`
  - `sf_voice.run(project_dir, only=None, config=None, client=None, root=ROOT, sleep=time.sleep) -> tuple[dict, int]`; summary `{"profiles": [cast ids], "done": [line ids], "skipped": int, "needs_human": [str], "errors": [str]}`
  - Writes `audio/<line>.wav`; sets `audio.{path, duration_ms, seed, used_seed, input_hash, status, attempts, qc, asr_words, last_error}`; sets `voice.profile_id` and `voice.instruct`.

- [ ] **Step 1: Write the failing tests**

`tests/test_sf_voice.py`:

```python
from fixtures import make_story, sine_wav_bytes, write_project
import sf_voice
from sflib.project import ProviderError, load_story
from sflib.text import display_text

CONFIG = {"voice": {"base_url": "http://vs.local", "engine": None, "qc": {"max_cer": 0.25, "min_cps": 2, "max_cps": 30}}}


class FakeVS:
    def __init__(self, bad_transcripts: int = 0, fail_generate: str | None = None):
        self.calls: list[dict] = []
        self.bad_left = bad_transcripts
        self.fail_generate = fail_generate
        self.profiles = 0

    def health(self):
        return None

    def describe(self, description):
        return {"attrs": {"Gender": "female"}, "instruct": "female"}

    def create_design_profile(self, name, attrs, instruct, language):
        self.profiles += 1
        return f"p{self.profiles}"

    def create_clone_profile(self, name, ref_audio, ref_text, language):
        raise AssertionError("not used")

    def generate(self, *, text, language, profile_id, seed, engine=None, instruct=None):
        self.calls.append({"text": text, "seed": seed, "instruct": instruct, "profile_id": profile_id, "language": language})
        if self.fail_generate:
            raise ProviderError(self.fail_generate, "refused")
        return sine_wav_bytes(1000), {"seed": str(seed), "duration_s": "1.0", "dropped_chunks": None}

    def transcribe_words(self, wav, language):
        if self.bad_left > 0:
            self.bad_left -= 1
            return [{"text": "zzz qqq", "start": 0.0, "end": 0.5}]
        words = display_text(self.calls[-1]["text"]).split()
        return [{"text": w, "start": i * 0.2, "end": i * 0.2 + 0.2} for i, w in enumerate(words)]


def test_cer():
    assert sf_voice.cer("Every night.", "every night") == 0.0
    assert sf_voice.cer("abcd", "abxd") == 0.25
    assert sf_voice.cer("", "") == 0.0


def test_creates_profiles_and_synthesizes_every_line(tmp_path):
    project = write_project(tmp_path, make_story())
    vs = FakeVS()
    summary, code = sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    assert code == 0
    assert summary["profiles"] == ["narrator", "C01"]
    assert summary["done"] == ["L001", "L002", "L003"]
    story = load_story(project)
    assert [c["voice"]["profile_id"] for c in story["cast"]] == ["p1", "p2"]
    audio = story["lines"][0]["audio"]
    assert audio["status"] == "done" and audio["path"] == "audio/L001.wav" and audio["duration_ms"] == 1000
    assert audio["seed"] == sf_voice.default_seed("demo-ch01-916-en", "L001")
    assert audio["qc"]["cer"] == 0.0 and audio["asr_words"][0]["text"] == "Every"
    whisper_call = vs.calls[2]
    assert whisper_call["text"] == "No. [sigh] Not again." and whisper_call["instruct"] == "female, whisper"
    assert vs.calls[0]["instruct"] is None and vs.calls[0]["language"] == "en"


def test_second_run_skips_everything(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_voice.run(project, config=CONFIG, client=FakeVS(), root=tmp_path)
    vs = FakeVS()
    summary, code = sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    assert code == 0 and summary["skipped"] == 3 and vs.calls == [] and vs.profiles == 0


def test_failed_qc_retakes_with_a_new_seed(tmp_path):
    project = write_project(tmp_path, make_story())
    vs = FakeVS(bad_transcripts=1)
    summary, code = sf_voice.run(project, config=CONFIG, client=vs, root=tmp_path)
    assert code == 0
    audio = load_story(project)["lines"][0]["audio"]
    assert audio["attempts"] == 2
    assert audio["used_seed"] == audio["seed"] + sf_voice.RETAKE_SEED_STEP


def test_persistent_qc_failure_needs_human(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_voice.run(project, config=CONFIG, client=FakeVS(bad_transcripts=100), root=tmp_path)
    assert code == 2
    audio = load_story(project)["lines"][0]["audio"]
    assert audio["status"] == "needs_human" and audio["attempts"] == 3
    assert "CER" in audio["last_error"]


def test_quota_stops_with_exit_3(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_voice.run(project, config=CONFIG, client=FakeVS(fail_generate="quota"), root=tmp_path)
    assert code == 3 and summary["errors"] == ["quota: refused"]


def test_library_voice_missing_needs_human(tmp_path):
    story = make_story()
    story["cast"][0]["voice"] = {"source": "library", "library_ref": "ghost", "profile_id": None}
    project = write_project(tmp_path, story)
    summary, code = sf_voice.run(project, config=CONFIG, client=FakeVS(), root=tmp_path)
    assert code == 2
    assert any("library voice" in item for item in summary["needs_human"])
    assert "L001" not in summary["done"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_sf_voice.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sf_voice'`

- [ ] **Step 3: Implement `scripts/sf_voice.py`**

```python
#!/usr/bin/env python3
"""Create voice profiles and synthesize every line through VoiceStudio, with transcribe-back QC."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Callable

from sflib.media import probe_duration_ms
from sflib.project import (
    EXIT_BUG, EXIT_HUMAN, EXIT_OK, EXIT_PROVIDER, ROOT, ProviderError, input_hash, load_config,
    load_story, log, main_wrapper, needs_work, save_story, wanted,
)
from sflib.text import display_text, norm
from sflib.voicestudio import VoiceStudio

MAX_RETAKES = 2
RETAKE_SEED_STEP = 7919
TRANSIENT_RETRIES = 3


def default_seed(slug: str, line_id: str) -> int:
    return int(hashlib.sha256(f"{slug}:{line_id}".encode()).hexdigest()[:8], 16) % 2_147_483_647


def cer(reference: str, hypothesis: str) -> float:
    ref = "".join(norm(reference).split())
    hyp = "".join(norm(hypothesis).split())
    if not ref:
        return 0.0 if not hyp else 1.0
    previous = list(range(len(hyp) + 1))
    for i, ref_char in enumerate(ref, 1):
        current = [i]
        for j, hyp_char in enumerate(hyp, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ref_char != hyp_char)))
        previous = current
    return previous[-1] / len(ref)


def _with_retries(call: Callable, sleep: Callable[[float], None]):
    for attempt in range(TRANSIENT_RETRIES + 1):
        try:
            return call()
        except ProviderError as exc:
            if exc.code != "transient" or attempt == TRANSIENT_RETRIES:
                raise
            sleep(2 ** attempt)


def _ensure_profiles(story: dict, vs, root: Path, project_dir: Path, summary: dict) -> None:
    language = story["brief"]["language"].split("-")[0]
    for member in story["cast"]:
        voice = member["voice"]
        if voice.get("profile_id"):
            continue
        name = f"{story['slug']}-{member['id']}"
        if voice["source"] == "library":
            ref = root / "library" / "cast" / voice["library_ref"] / "voice.json"
            if not ref.exists():
                summary["needs_human"].append(f"{member['id']}: library voice {ref} is missing")
                continue
            library = json.loads(ref.read_text(encoding="utf-8"))
            voice["profile_id"] = library["profile_id"]
            voice["instruct"] = library.get("instruct", "")
        elif voice["source"] == "design":
            parsed = vs.describe(voice["design_prompt"])
            voice["instruct"] = parsed.get("instruct", "")
            voice["profile_id"] = vs.create_design_profile(name, parsed.get("attrs", {}), voice["instruct"], language)
        else:
            voice["profile_id"] = vs.create_clone_profile(name, root / voice["ref_audio"], voice.get("ref_text", ""), language)
            voice["instruct"] = ""
        summary["profiles"].append(member["id"])
        save_story(project_dir, story)


def _quality(vs, wav: Path, line: dict, language: str, duration_ms: int, meta: dict, qc_cfg: dict) -> tuple[dict, list | None]:
    shown = display_text(line["text"])
    cps = len("".join(norm(shown).split())) / max(duration_ms / 1000, 0.001)
    qc: dict = {"cps": round(cps, 2), "cer": None, "asr": "ok", "reasons": []}
    if meta.get("dropped_chunks"):
        qc["reasons"].append("VoiceStudio dropped part of the text")
    if not qc_cfg["min_cps"] <= cps <= qc_cfg["max_cps"]:
        qc["reasons"].append(f"speaking rate {cps:.1f} chars/s outside [{qc_cfg['min_cps']}, {qc_cfg['max_cps']}]")
    words = None
    try:
        words = vs.transcribe_words(wav, language)
    except ProviderError as exc:
        qc["asr"] = f"skipped: {exc.code}: {exc.message}"
    if words is not None:
        error = cer(shown, " ".join(word["text"] for word in words))
        qc["cer"] = round(error, 3)
        if error > qc_cfg["max_cer"]:
            qc["reasons"].append(f"transcribe-back CER {error:.2f} > {qc_cfg['max_cer']}")
    return qc, words


def run(project_dir: Path, only: set[str] | None = None, config: dict | None = None, client=None,
        root: Path = ROOT, sleep: Callable[[float], None] = time.sleep) -> tuple[dict, int]:
    config = config or load_config()
    voice_cfg = config["voice"]
    vs = client or VoiceStudio(voice_cfg["base_url"])
    story = load_story(project_dir)
    summary: dict = {"profiles": [], "done": [], "skipped": 0, "needs_human": [], "errors": []}
    language = story["brief"]["language"].split("-")[0]
    engine = voice_cfg.get("engine")
    cast = {member["id"]: member for member in story["cast"]}
    try:
        vs.health()
        _ensure_profiles(story, vs, root, project_dir, summary)
        for line in story["lines"]:
            if not wanted(line["id"], only):
                continue
            member = cast[line["speaker"]]
            profile_id = member["voice"].get("profile_id")
            if not profile_id:
                summary["needs_human"].append(f"{line['id']}: speaker {member['id']} has no voice profile")
                continue
            audio = line["audio"]
            base_seed = audio["seed"] if audio.get("seed") is not None else default_seed(story["slug"], line["id"])
            whisper = bool(line.get("whisper"))
            instruct = ", ".join(p for p in (member["voice"].get("instruct"), "whisper") if p) if whisper else None
            new_hash = input_hash({"text": line["text"], "profile": profile_id, "whisper": whisper,
                                   "language": language, "engine": engine, "seed": base_seed})
            if only is None and not needs_work(audio, new_hash, project_dir):
                summary["skipped"] += 1
                continue
            if audio.get("input_hash") != new_hash:
                audio["attempts"] = 0
            rel_path = f"audio/{line['id']}.wav"
            wav = project_dir / rel_path
            wav.parent.mkdir(exist_ok=True)
            for take in range(MAX_RETAKES + 1):
                seed = base_seed + take * RETAKE_SEED_STEP
                data, meta = _with_retries(lambda: vs.generate(text=line["text"], language=language, profile_id=profile_id,
                                                                seed=seed, engine=engine, instruct=instruct), sleep)
                wav.write_bytes(data)
                duration = probe_duration_ms(wav)
                qc, words = _quality(vs, wav, line, language, duration, meta, voice_cfg["qc"])
                audio["attempts"] = audio.get("attempts", 0) + 1
                if not qc["reasons"]:
                    break
            passed = not qc["reasons"]
            audio.update(path=rel_path, duration_ms=duration, seed=base_seed, used_seed=seed, input_hash=new_hash,
                         status="done" if passed else "needs_human", qc=qc, asr_words=words,
                         last_error=None if passed else "; ".join(qc["reasons"]))
            (summary["done"] if passed else summary["needs_human"]).append(line["id"])
            log(project_dir, "sf_voice", f"{line['id']}: {audio['status']} seed={seed} qc={qc}")
            save_story(project_dir, story)
    except ProviderError as exc:
        save_story(project_dir, story)
        summary["errors"].append(f"{exc.code}: {exc.message}")
        if exc.code in ("quota", "auth"):
            return summary, EXIT_PROVIDER
        if exc.code == "transient":
            return summary, EXIT_HUMAN
        return summary, EXIT_BUG
    return summary, EXIT_HUMAN if summary["needs_human"] else EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_sf_voice.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/sf_voice.py tests/test_sf_voice.py
git commit -m "$(cat <<'EOF'
Add sf_voice: profiles, per-line synthesis, transcribe-back QC and retakes

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 9: `sf_align`

**Files:**
- Create: `scripts/sf_align.py`, `tests/test_sf_align.py`

**Interfaces:**
- Consumes: `sflib.project`, `sflib.text` (`clusters`, `norm`, `tokens`, `uses_clusters`), `sflib.voicestudio.VoiceStudio` (only when `audio.asr_words` is null)
- Produces:
  - `sf_align.align_line(script_tokens: list[str], asr_words: list[dict], duration_ms: int, language: str) -> list[dict]` → `[{"text", "start_ms", "end_ms", "approx"}]`, relative to the line start, monotonic, clamped to `[0, duration_ms]`
  - `sf_align.run(project_dir, only=None, config=None, client=None) -> tuple[dict, int]`; summary `{"aligned": [ids], "skipped": int, "needs_human": [str], "approx_ratio": float}`; sets `words` and `words_hash = audio.input_hash`

- [ ] **Step 1: Write the failing tests**

`tests/test_sf_align.py`:

```python
from fixtures import make_story, write_project
import sf_align
from sflib.project import load_story, save_story
from sflib.text import tokens


def _w(text, start, end):
    return {"text": text, "start": start, "end": end}


def _times(words):
    return [(w["text"], w["start_ms"], w["end_ms"], w["approx"]) for w in words]


def test_exact_match_takes_asr_times():
    asr = [_w("Every", 0.0, 0.3), _w("night", 0.3, 0.6), _w("for", 0.6, 0.8), _w("eleven", 0.8, 1.2), _w("years.", 1.2, 1.5)]
    words = sf_align.align_line(["Every", "night", "for", "eleven", "years."], asr, 1500, "en")
    assert _times(words) == [("Every", 0, 300, False), ("night", 300, 600, False), ("for", 600, 800, False),
                             ("eleven", 800, 1200, False), ("years.", 1200, 1500, False)]


def test_substitution_of_equal_length_maps_pairwise():
    asr = [_w("The", 0.0, 0.2), _w("color", 0.2, 0.6), _w("red", 0.6, 0.9)]
    words = sf_align.align_line(["The", "colour", "red"], asr, 900, "en")
    assert _times(words)[1] == ("colour", 200, 600, False)


def test_missing_word_is_interpolated_and_flagged():
    asr = [_w("I", 0.0, 0.2), _w("know", 0.6, 0.9)]
    words = sf_align.align_line(["I", "really", "know"], asr, 900, "en")
    assert _times(words) == [("I", 0, 200, False), ("really", 200, 600, True), ("know", 600, 900, False)]


def test_no_asr_falls_back_to_length_weighted_split():
    words = sf_align.align_line(["ab", "abcd"], [], 600, "en")
    assert _times(words) == [("ab", 0, 200, True), ("abcd", 200, 600, True)]


def test_cluster_language_splits_asr_words():
    asr = [_w("你好", 0.0, 0.4), _w("世界", 0.5, 0.9)]
    words = sf_align.align_line(tokens("你好，世界", "zh"), asr, 900, "zh")
    assert _times(words) == [("你", 0, 200, False), ("好，", 200, 400, False), ("世", 500, 700, False), ("界", 700, 900, False)]


def test_times_are_monotonic_and_clamped():
    asr = [_w("a", 0.5, 0.7), _w("b", 0.2, 0.3), _w("c", 0.9, 5.0)]
    words = sf_align.align_line(["a", "b", "c"], asr, 1000, "en")
    starts = [w["start_ms"] for w in words]
    assert starts == sorted(starts)
    assert all(0 <= w["start_ms"] <= w["end_ms"] <= 1000 for w in words)


def test_run_uses_stored_asr_words_and_skips_when_current(tmp_path):
    story = make_story()
    for line in story["lines"]:
        text_tokens = tokens(line["text"], "en")
        line["audio"].update(status="done", path=f"audio/{line['id']}.wav", duration_ms=1000, input_hash=f"h-{line['id']}",
                             asr_words=[_w(t, i * 0.2, i * 0.2 + 0.2) for i, t in enumerate(text_tokens)])
    project = write_project(tmp_path, story)
    summary, code = sf_align.run(project)
    assert code == 0 and summary["aligned"] == ["L001", "L002", "L003"] and summary["approx_ratio"] == 0.0
    stored = load_story(project)["lines"][2]
    assert [w["text"] for w in stored["words"]] == ["No.", "Not", "again."]
    assert stored["words_hash"] == "h-L003"
    summary, _ = sf_align.run(project)
    assert summary["aligned"] == [] and summary["skipped"] == 3


def test_run_reports_lines_without_audio(tmp_path):
    project = write_project(tmp_path, make_story())
    summary, code = sf_align.run(project)
    assert code == 2 and summary["needs_human"] == ["L001 has no audio", "L002 has no audio", "L003 has no audio"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_sf_align.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sf_align'`

- [ ] **Step 3: Implement `scripts/sf_align.py`**

```python
#!/usr/bin/env python3
"""Align script tokens to ASR word timings; captions always show script text."""
from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path

from sflib.project import EXIT_HUMAN, EXIT_OK, ProviderError, load_config, load_story, main_wrapper, save_story, wanted
from sflib.text import clusters, norm, tokens, uses_clusters
from sflib.voicestudio import VoiceStudio

MIN_MATCH_RATIO = 0.3


def _units(asr_words: list[dict], language: str) -> list[dict]:
    units = []
    for word in asr_words:
        parts = clusters(word["text"]) if uses_clusters(language) else word["text"].split()
        parts = [part for part in parts if norm(part)]
        if not parts:
            continue
        start, end = word.get("start"), word.get("end")
        if start is None or end is None or end < start:
            units += [{"key": norm(part), "start": None, "end": None} for part in parts]
            continue
        step = (end - start) / len(parts)
        for index, part in enumerate(parts):
            units.append({"key": norm(part), "start": start + index * step, "end": start + (index + 1) * step})
    return units


def _weights(script_tokens: list[str]) -> list[int]:
    return [max(1, len(norm(token))) for token in script_tokens]


def _split(script_tokens: list[str], start: int, end: int) -> list[tuple[int, int]]:
    weights = _weights(script_tokens)
    total = sum(weights)
    spans, cursor = [], 0
    for weight in weights:
        span_start = start + round((end - start) * cursor / total)
        cursor += weight
        spans.append((span_start, start + round((end - start) * cursor / total)))
    return spans


def align_line(script_tokens: list[str], asr_words: list[dict], duration_ms: int, language: str) -> list[dict]:
    if not script_tokens:
        return []
    units = _units(asr_words or [], language)
    keys = [norm(token) for token in script_tokens]
    times: list[tuple[int, int] | None] = [None] * len(script_tokens)
    matcher = SequenceMatcher(None, keys, [unit["key"] for unit in units], autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            for offset in range(i2 - i1):
                unit = units[j1 + offset]
                if unit["start"] is not None and keys[i1 + offset]:
                    times[i1 + offset] = (round(unit["start"] * 1000), round(unit["end"] * 1000))
    matched = sum(t is not None for t in times)
    approx = [t is None for t in times]
    if matched == 0 or matched < MIN_MATCH_RATIO * len(script_tokens):
        spans = _split(script_tokens, 0, duration_ms)
        approx = [True] * len(script_tokens)
    else:
        spans = list(times)
        index = 0
        while index < len(spans):
            if spans[index] is not None:
                index += 1
                continue
            run_end = index
            while run_end < len(spans) and spans[run_end] is None:
                run_end += 1
            left = spans[index - 1][1] if index > 0 else 0
            right = spans[run_end][0] if run_end < len(spans) else duration_ms
            spans[index:run_end] = _split(script_tokens[index:run_end], left, max(left, right))
            index = run_end
    words, previous_start = [], 0
    for token, (start, end), is_approx in zip(script_tokens, spans, approx):
        start = min(max(start, previous_start), duration_ms)
        end = min(max(end, start), duration_ms)
        previous_start = start
        words.append({"text": token, "start_ms": start, "end_ms": end, "approx": is_approx})
    return words


def run(project_dir: Path, only: set[str] | None = None, config: dict | None = None, client=None) -> tuple[dict, int]:
    story = load_story(project_dir)
    language = story["brief"]["language"]
    summary: dict = {"aligned": [], "skipped": 0, "needs_human": [], "approx_ratio": 0.0}
    vs = client
    for line in story["lines"]:
        if not wanted(line["id"], only):
            continue
        audio = line["audio"]
        if audio.get("status") != "done" or not audio.get("duration_ms"):
            summary["needs_human"].append(f"{line['id']} has no audio")
            continue
        if only is None and line.get("words") and line.get("words_hash") == audio["input_hash"]:
            summary["skipped"] += 1
            continue
        asr_words = audio.get("asr_words")
        if asr_words is None:
            if vs is None:
                vs = VoiceStudio((config or load_config())["voice"]["base_url"])
            try:
                asr_words = vs.transcribe_words(project_dir / audio["path"], language.split("-")[0])
            except ProviderError:
                asr_words = []
        line["words"] = align_line(tokens(line["text"], language), asr_words, audio["duration_ms"], language)
        line["words_hash"] = audio["input_hash"]
        summary["aligned"].append(line["id"])
    save_story(project_dir, story)
    all_words = [word for line in story["lines"] for word in line.get("words") or []]
    if all_words:
        summary["approx_ratio"] = round(sum(word["approx"] for word in all_words) / len(all_words), 3)
    return summary, EXIT_HUMAN if summary["needs_human"] else EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_sf_align.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add scripts/sf_align.py tests/test_sf_align.py
git commit -m "$(cat <<'EOF'
Add sf_align: transfer ASR word times onto script tokens

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 10: Caption styles and `sf_captions`

**Files:**
- Create: `config/caption-styles/karaoke-bold.yaml`, `config/caption-styles/subtitle-clean.yaml`, `scripts/sf_captions.py`, `tests/test_sf_captions.py`

**Interfaces:**
- Consumes: `sflib.project`, `sflib.timeline.build_timeline`, `sflib.text.uses_clusters`
- Produces:
  - Style YAML keys: `font`, `bold`, `font_size.{9:16,16:9}`, `outline`, `shadow`, `unsung_color`, `max_chars_per_line.{9:16,16:9}`, `max_lines`, `margin_v_pct.{9:16,16:9}.{lower_third,center,upper_third}`
  - `sf_captions.SIZE = {"9:16": (1080, 1920), "16:9": (1920, 1080)}`
  - `sf_captions.ass_color(hex_rgb: str) -> str` (`#FFD166` → `&H0066D1FF`)
  - `sf_captions.ass_time(ms: int) -> str` (`1500` → `0:00:01.50`)
  - `sf_captions.load_style(name: str, styles_dir: Path = STYLES_DIR) -> dict`
  - `sf_captions.run(project_dir, only=None, styles_dir=STYLES_DIR) -> tuple[dict, int]`; writes `out/captions.ass`; sets `output.captions`; summary `{"mode", "cues": int, "needs_human": [str]}`

- [ ] **Step 1: Write the style presets**

`config/caption-styles/karaoke-bold.yaml`:

```yaml
# Word-by-word highlight. Unsung words use unsung_color; sung words take the speaker's caption_color.
font: Arial
bold: true
font_size: {"9:16": 78, "16:9": 60}
outline: 5
shadow: 0
unsung_color: "#9A9A9A"
max_chars_per_line: {"9:16": 18, "16:9": 36}
max_lines: 2
margin_v_pct:
  "9:16": {lower_third: 0.22, center: 0.0, upper_third: 0.14}
  "16:9": {lower_third: 0.10, center: 0.0, upper_third: 0.10}
```

`config/caption-styles/subtitle-clean.yaml`:

```yaml
# Classic subtitles in the speaker's caption_color.
font: Arial
bold: false
font_size: {"9:16": 64, "16:9": 48}
outline: 3
shadow: 0
unsung_color: "#FFFFFF"
max_chars_per_line: {"9:16": 22, "16:9": 42}
max_lines: 2
margin_v_pct:
  "9:16": {lower_third: 0.20, center: 0.0, upper_third: 0.12}
  "16:9": {lower_third: 0.08, center: 0.0, upper_third: 0.08}
```

- [ ] **Step 2: Write the failing tests**

`tests/test_sf_captions.py`:

```python
from fixtures import make_story, write_project
import sf_captions
from sflib.project import ROOT, load_story

STYLES = ROOT / "config" / "caption-styles"

WORDS = {
    "L001": [("Every", 0, 300), ("night", 300, 600), ("for", 600, 800), ("eleven", 800, 1200), ("years.", 1200, 1500)],
    "L002": [("Every", 0, 300), ("single", 300, 600), ("night.", 600, 900)],
    "L003": [("No.", 0, 400), ("Not", 600, 900), ("again.", 900, 1300)],
}
DURATIONS = {"L001": 1500, "L002": 900, "L003": 1300}


def _project(tmp_path, mode="karaoke", style="karaoke-bold"):
    story = make_story()
    story["brief"]["captions"] = {"mode": mode, "style": style}
    for line in story["lines"]:
        line["audio"].update(status="done", duration_ms=DURATIONS[line["id"]], input_hash=f"h-{line['id']}")
        line["words"] = [{"text": t, "start_ms": s, "end_ms": e, "approx": False} for t, s, e in WORDS[line["id"]]]
        line["words_hash"] = f"h-{line['id']}"
    return write_project(tmp_path, story)


def test_helpers():
    assert sf_captions.ass_color("#FFD166") == "&H0066D1FF"
    assert sf_captions.ass_time(1500) == "0:00:01.50"
    assert sf_captions.ass_time(3_723_450) == "1:02:03.45"


def test_karaoke_ass(tmp_path):
    project = _project(tmp_path)
    summary, code = sf_captions.run(project, styles_dir=STYLES)
    assert code == 0 and summary["cues"] == 3
    ass = (project / "out/captions.ass").read_text(encoding="utf-8")
    assert "PlayResX: 1080\nPlayResY: 1920" in ass
    assert "Style: narrator,Arial,78,&H00FFFFFF,&H009A9A9A,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,2,60,60,0,1" in ass
    assert "Style: C01,Arial,78,&H0066D1FF,&H009A9A9A," in ass
    assert ("Dialogue: 0,0:00:00.00,0:00:01.50,narrator,,0,0,422,,"
            "{\\an2}{\\kf30}Every {\\kf30}night {\\kf20}for\\N{\\kf40}eleven {\\kf30}years.") in ass
    assert "Dialogue: 0,0:00:02.65,0:00:03.95,C01,,0,0,422,,{\\an2}{\\kf60}No. {\\kf30}Not {\\kf40}again." in ass
    assert load_story(project)["output"]["captions"] == "out/captions.ass"


def test_plain_ass(tmp_path):
    project = _project(tmp_path, mode="plain", style="subtitle-clean")
    sf_captions.run(project, styles_dir=STYLES)
    ass = (project / "out/captions.ass").read_text(encoding="utf-8")
    assert "Dialogue: 0,0:00:00.00,0:00:01.50,narrator,,0,0,384,,{\\an2}Every night for\\Neleven years." in ass


def test_mode_none_writes_nothing(tmp_path):
    project = _project(tmp_path, mode="none")
    summary, code = sf_captions.run(project, styles_dir=STYLES)
    assert code == 0 and summary["cues"] == 0
    assert not (project / "out/captions.ass").exists()
    assert load_story(project)["output"]["captions"] is None


def test_stale_words_need_alignment(tmp_path):
    project = _project(tmp_path)
    story = load_story(project)
    story["lines"][1]["words_hash"] = "old"
    from sflib.project import save_story
    save_story(project, story)
    summary, code = sf_captions.run(project, styles_dir=STYLES)
    assert code == 2 and summary["needs_human"] == ["L002: words are missing or stale; run sf_align"]
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/test_sf_captions.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sf_captions'`

- [ ] **Step 4: Implement `scripts/sf_captions.py`**

```python
#!/usr/bin/env python3
"""Build out/captions.ass (karaoke or plain) from aligned words and the timeline."""
from __future__ import annotations

from pathlib import Path

import yaml

from sflib.project import EXIT_HUMAN, EXIT_OK, ROOT, load_story, main_wrapper, save_story
from sflib.text import uses_clusters
from sflib.timeline import build_timeline

STYLES_DIR = ROOT / "config" / "caption-styles"
SIZE = {"9:16": (1080, 1920), "16:9": (1920, 1080)}
ALIGNMENT = {"lower_third": 2, "center": 5, "upper_third": 8}
SENTENCE_END = (".", "!", "?", "…", "。", "！", "？")
MARGIN_LR = 60


def ass_color(hex_rgb: str) -> str:
    red, green, blue = hex_rgb[1:3], hex_rgb[3:5], hex_rgb[5:7]
    return f"&H00{blue}{green}{red}".upper()


def ass_time(ms: int) -> str:
    cs = round(ms / 10)
    return f"{cs // 360000}:{(cs // 6000) % 60:02d}:{(cs // 100) % 60:02d}.{cs % 100:02d}"


def load_style(name: str, styles_dir: Path = STYLES_DIR) -> dict:
    return yaml.safe_load((styles_dir / f"{name}.yaml").read_text(encoding="utf-8"))


def _escape(text: str) -> str:
    return text.replace("\\", "/").replace("{", "(").replace("}", ")")


def _joined_len(words: list[dict], spaced: bool) -> int:
    return sum(len(w["text"]) for w in words) + (len(words) - 1 if spaced else 0)


def _chunk(words: list[dict], limit: int, spaced: bool) -> list[list[dict]]:
    cues, current = [], []
    for word in words:
        if current and _joined_len(current + [word], spaced) > limit:
            cues.append(current)
            current = []
        current.append(word)
        if word["text"].endswith(SENTENCE_END) and _joined_len(current, spaced) >= limit / 2:
            cues.append(current)
            current = []
    if current:
        cues.append(current)
    return cues


def _split_lines(cue: list[dict], max_chars: int, spaced: bool) -> list[list[dict]]:
    if _joined_len(cue, spaced) <= max_chars or len(cue) == 1:
        return [cue]
    best = min(range(1, len(cue)), key=lambda k: abs(_joined_len(cue[:k], spaced) - _joined_len(cue[k:], spaced)))
    return [cue[:best], cue[best:]]


def _cue_text(rows: list[list[dict]], karaoke: bool, spaced: bool) -> str:
    flat = [word for row in rows for word in row]
    durations = {}
    for index, word in enumerate(flat):
        until = flat[index + 1]["start_ms"] if index + 1 < len(flat) else word["end_ms"]
        durations[id(word)] = max(0, round((until - word["start_ms"]) / 10))
    joiner = " " if spaced else ""
    rendered = []
    for row in rows:
        if karaoke:
            rendered.append(joiner.join(f"{{\\kf{durations[id(w)]}}}{_escape(w['text'])}" for w in row))
        else:
            rendered.append(joiner.join(_escape(w["text"]) for w in row))
    return "\\N".join(rendered)


def _header(story: dict, style: dict) -> str:
    aspect = story["brief"]["aspect"]
    width, height = SIZE[aspect]
    bold = -1 if style["bold"] else 0
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {width}", f"PlayResY: {height}",
        "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding",
    ]
    for member in story["cast"]:
        lines.append(
            f"Style: {member['id']},{style['font']},{style['font_size'][aspect]},{ass_color(member['caption_color'])},"
            f"{ass_color(style['unsung_color'])},&H00000000,&H80000000,{bold},0,0,0,100,100,0,0,1,"
            f"{style['outline']},{style['shadow']},2,{MARGIN_LR},{MARGIN_LR},0,1"
        )
    lines += ["", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    return "\n".join(lines)


def run(project_dir: Path, only: set[str] | None = None, styles_dir: Path = STYLES_DIR) -> tuple[dict, int]:
    story = load_story(project_dir)
    mode = story["brief"]["captions"]["mode"]
    if mode == "none":
        story["output"]["captions"] = None
        save_story(project_dir, story)
        return {"mode": mode, "cues": 0, "needs_human": []}, EXIT_OK
    stale = [f"{line['id']}: words are missing or stale; run sf_align" for line in story["lines"]
             if not line.get("words") or line.get("words_hash") != line["audio"].get("input_hash")]
    if stale:
        return {"mode": mode, "cues": 0, "needs_human": stale}, EXIT_HUMAN
    style = load_style(story["brief"]["captions"]["style"], styles_dir)
    aspect = story["brief"]["aspect"]
    height = SIZE[aspect][1]
    spaced = not uses_clusters(story["brief"]["language"])
    max_chars = style["max_chars_per_line"][aspect]
    timeline = build_timeline(story)
    placement = {lid: slide["visual"]["text_placement"] for slide in story["slides"] for lid in slide["line_ids"]}
    events = []
    for line in story["lines"]:
        start = timeline.line_start_ms[line["id"]]
        where = placement[line["id"]]
        margin_v = round(style["margin_v_pct"][aspect][where] * height)
        for cue in _chunk(line["words"], max_chars * style["max_lines"], spaced):
            rows = _split_lines(cue, max_chars, spaced)
            cue_start = start + cue[0]["start_ms"]
            cue_end = max(start + cue[-1]["end_ms"], cue_start + 10)
            text = f"{{\\an{ALIGNMENT[where]}}}" + _cue_text(rows, mode == "karaoke", spaced)
            events.append(f"Dialogue: 0,{ass_time(cue_start)},{ass_time(cue_end)},{line['speaker']},,0,0,{margin_v},,{text}")
    out = project_dir / "out" / "captions.ass"
    out.parent.mkdir(exist_ok=True)
    out.write_text(_header(story, style) + "\n" + "\n".join(events) + "\n", encoding="utf-8")
    story["output"]["captions"] = "out/captions.ass"
    save_story(project_dir, story)
    return {"mode": mode, "cues": len(events), "needs_human": []}, EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run pytest tests/test_sf_captions.py -v`
Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add config/caption-styles scripts/sf_captions.py tests/test_sf_captions.py
git commit -m "$(cat <<'EOF'
Add caption style presets and sf_captions ASS builder

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 11: `sf_render`

**Files:**
- Create: `scripts/sf_render.py`, `tests/test_sf_render.py`
- Modify: `tests/fixtures.py` (add `prepare_media`)

**Interfaces:**
- Consumes: `sflib.project`, `sflib.timeline` (`FPS`, `build_timeline`), `sflib.media` (`decode_pcm`, `has_filter`, `run_ffmpeg`), `sf_image.run` and `sf_align.align_line` (tests only)
- Produces:
  - `sf_render.SIZE = {"9:16": (1080, 1920), "16:9": (1920, 1080)}`
  - `sf_render.motion_filter(motion: str, frames: int, width: int, height: int) -> str`
  - `sf_render.run(project_dir, only=None, size: tuple[int, int] | None = None) -> tuple[dict, int]`; writes `clips/<slide>.mp4`, `clips/manifest.json`, `clips/timeline.wav`, `out/final.mp4`; sets `output.video`; summary `{"video", "frames", "duration_ms", "rendered": [ids], "cached": int, "needs_human": [str]}`
- Produces (in `tests/fixtures.py`): `prepare_media(root: Path, story: dict, durations: list[int]) -> Path`

- [ ] **Step 1: Add `prepare_media` to `tests/fixtures.py`**

Add at the end of the file:

```python
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
```

- [ ] **Step 2: Write the failing tests**

`tests/test_sf_render.py`:

```python
import pytest

from fixtures import make_story, prepare_media
import sf_captions
import sf_render
from sflib.media import probe_audio_ms, probe_video
from sflib.project import ROOT, load_story
from sflib.timeline import build_timeline

SMALL = (360, 640)


def test_motion_filter_expressions():
    vf = sf_render.motion_filter("push_in", 60, 360, 640)
    assert vf.startswith("scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,")
    assert "zoompan=z='1+0.08*on/60'" in vf and ":d=60:s=360x640:fps=30" in vf
    assert "x='(iw-iw/zoom)*on/60'" in sf_render.motion_filter("pan_right", 60, 360, 640)
    with pytest.raises(ValueError):
        sf_render.motion_filter("spin", 60, 360, 640)


def test_render_matches_the_timeline_and_caches_clips(tmp_path):
    story = make_story()
    story["brief"]["captions"]["mode"] = "none"
    project = prepare_media(tmp_path, story, [1000, 700, 1300])
    summary, code = sf_render.run(project, size=SMALL)
    assert code == 0 and summary["rendered"] == ["S01", "S02"]
    timeline = build_timeline(load_story(project))
    video = probe_video(project / "out/final.mp4")
    assert (video["width"], video["height"]) == SMALL
    assert video["frames"] == timeline.total_frames == summary["frames"]
    assert abs(probe_audio_ms(project / "out/final.mp4") - timeline.total_ms) <= 60
    assert load_story(project)["output"]["video"] == "out/final.mp4"
    summary, _ = sf_render.run(project, size=SMALL)
    assert summary["rendered"] == [] and summary["cached"] == 2


def test_render_burns_captions(tmp_path):
    project = prepare_media(tmp_path, make_story(), [1000, 700, 1300])
    sf_captions.run(project, styles_dir=ROOT / "config" / "caption-styles")
    summary, code = sf_render.run(project, size=SMALL)
    assert code == 0
    assert probe_video(project / "out/final.mp4")["frames"] == summary["frames"]


def test_missing_assets_need_human(tmp_path):
    project = prepare_media(tmp_path, make_story(), [1000, 700, 1300])
    (project / "images/S02.png").unlink()
    summary, code = sf_render.run(project, size=SMALL)
    assert code == 2
    assert summary["needs_human"] == ["S02: image missing", "captions are not built; run sf_captions"]
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/test_sf_render.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sf_render'`

- [ ] **Step 4: Implement `scripts/sf_render.py`**

```python
#!/usr/bin/env python3
"""Render out/final.mp4: per-slide motion clips, a sample-exact audio timeline, and burned-in captions."""
from __future__ import annotations

import json
import wave
from pathlib import Path

from sflib.media import decode_pcm, has_filter, run_ffmpeg
from sflib.project import EXIT_HUMAN, EXIT_OK, file_hash, input_hash, load_story, main_wrapper, save_story
from sflib.timeline import FPS, build_timeline

SIZE = {"9:16": (1080, 1920), "16:9": (1920, 1080)}
ZOOM = 0.08
RATE = 48000


def motion_filter(motion: str, frames: int, width: int, height: int) -> str:
    n = frames
    center_x, center_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if motion == "static":
        z, x, y = "1", center_x, center_y
    elif motion == "push_in":
        z, x, y = f"1+{ZOOM}*on/{n}", center_x, center_y
    elif motion == "pull_out":
        z, x, y = f"{1 + ZOOM}-{ZOOM}*on/{n}", center_x, center_y
    elif motion == "pan_left":
        z, x, y = f"{1 + ZOOM}", f"(iw-iw/zoom)*(1-on/{n})", center_y
    elif motion == "pan_right":
        z, x, y = f"{1 + ZOOM}", f"(iw-iw/zoom)*on/{n}", center_y
    else:
        raise ValueError(f"unknown motion {motion!r}")
    return (f"scale={width * 2}:{height * 2}:force_original_aspect_ratio=increase,crop={width * 2}:{height * 2},"
            f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={width}x{height}:fps={FPS},setsar=1,format=yuv420p")


def _missing(story: dict, project_dir: Path) -> list[str]:
    missing = []
    for slide in story["slides"]:
        image = slide["image"]
        if image.get("status") != "done" or not (project_dir / (image.get("path") or "")).is_file():
            missing.append(f"{slide['id']}: image missing")
    for line in story["lines"]:
        audio = line["audio"]
        if audio.get("status") != "done" or not (project_dir / (audio.get("path") or "")).is_file():
            missing.append(f"{line['id']}: audio missing")
    return missing


def _write_timeline_wav(story: dict, timeline, project_dir: Path, out: Path) -> None:
    buffer = bytearray(round(timeline.total_ms * RATE / 1000) * 2)
    for line in story["lines"]:
        pcm = decode_pcm(project_dir / line["audio"]["path"], RATE)
        offset = round(timeline.line_start_ms[line["id"]] * RATE / 1000) * 2
        end = min(offset + len(pcm), len(buffer))
        buffer[offset:end] = pcm[: end - offset]
    with wave.open(str(out), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(bytes(buffer))


def run(project_dir: Path, only: set[str] | None = None, size: tuple[int, int] | None = None) -> tuple[dict, int]:
    story = load_story(project_dir)
    summary: dict = {"video": None, "frames": 0, "duration_ms": 0, "rendered": [], "cached": 0, "needs_human": []}
    missing = _missing(story, project_dir)
    captions = None
    if story["brief"]["captions"]["mode"] != "none":
        captions = story["output"].get("captions")
        if not captions or not (project_dir / captions).is_file():
            missing.append("captions are not built; run sf_captions")
        elif not has_filter("ass"):
            missing.append("ffmpeg has no 'ass' filter; install an ffmpeg build with libass")
    if missing:
        summary["needs_human"] = missing
        return summary, EXIT_HUMAN
    width, height = size or SIZE[story["brief"]["aspect"]]
    timeline = build_timeline(story)
    clips = project_dir / "clips"
    clips.mkdir(exist_ok=True)
    manifest_path = clips / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    slides = {slide["id"]: slide for slide in story["slides"]}
    for span in timeline.slides:
        slide = slides[span.slide_id]
        if span.frames < 1:
            raise ValueError(f"{span.slide_id} spans {span.frames} frames; its lines are too short")
        image = project_dir / slide["image"]["path"]
        clip = clips / f"{span.slide_id}.mp4"
        clip_hash = input_hash({"image": file_hash(image), "motion": slide["visual"]["motion"],
                                "frames": span.frames, "size": [width, height]})
        if manifest.get(span.slide_id) == clip_hash and clip.is_file() and (only is None or span.slide_id not in only):
            summary["cached"] += 1
            continue
        run_ffmpeg(["-i", str(image), "-vf", motion_filter(slide["visual"]["motion"], span.frames, width, height),
                    "-frames:v", str(span.frames), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-r", str(FPS), str(clip)])
        manifest[span.slide_id] = clip_hash
        summary["rendered"].append(span.slide_id)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    (clips / "concat.txt").write_text("".join(f"file '{span.slide_id}.mp4'\n" for span in timeline.slides))
    _write_timeline_wav(story, timeline, project_dir, clips / "timeline.wav")
    (project_dir / "out").mkdir(exist_ok=True)
    args = ["-f", "concat", "-safe", "0", "-i", "clips/concat.txt", "-i", "clips/timeline.wav"]
    if captions:
        args += ["-vf", f"ass={captions}"]
    args += ["-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", "-r", str(FPS), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
             "-ar", str(RATE), "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "out/final.mp4"]
    run_ffmpeg(args, cwd=project_dir)
    story["output"]["video"] = "out/final.mp4"
    save_story(project_dir, story)
    summary.update(video="out/final.mp4", frames=timeline.total_frames, duration_ms=timeline.total_ms)
    return summary, EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run pytest tests/test_sf_render.py -v`
Expected: 4 passed (the render tests take several seconds each)

- [ ] **Step 6: Commit**

```bash
git add scripts/sf_render.py tests/test_sf_render.py tests/fixtures.py
git commit -m "$(cat <<'EOF'
Add sf_render: cached motion clips, sample-exact audio, caption burn-in

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 12: `sf_qc`

**Files:**
- Create: `scripts/sf_qc.py`, `tests/test_sf_qc.py`

**Interfaces:**
- Consumes: `sflib.project`, `sflib.timeline.build_timeline`, `sflib.media` (`probe_video`, `probe_audio_ms`, `silences`), `sf_captions.load_style`, `sf_captions.SIZE`
- Produces: `sf_qc.run(project_dir, only=None, size=None, styles_dir=STYLES_DIR) -> tuple[dict, int]`; writes `out/qc.json` = `{"checks": [{"name", "ok", "detail"}], "approx_ratio": float}`; sets `output.qc`; summary `{"failed": [check names], "approx_ratio": float}`; exit `2` when any check fails. Check names: `assets_done`, `frames_match`, `audio_duration`, `resolution`, `caption_timing`, `caption_line_length`, `silence`.

- [ ] **Step 1: Write the failing tests**

`tests/test_sf_qc.py`:

```python
import json

from fixtures import make_story, prepare_media
import sf_captions
import sf_qc
import sf_render
from sflib.project import ROOT, load_story, save_story

SMALL = (360, 640)
STYLES = ROOT / "config" / "caption-styles"


def _rendered(tmp_path):
    project = prepare_media(tmp_path, make_story(), [1000, 700, 1300])
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    return project


def test_clean_render_passes_every_check(tmp_path):
    project = _rendered(tmp_path)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 0, summary
    report = json.loads((project / "out/qc.json").read_text())
    assert [c["name"] for c in report["checks"]] == [
        "assets_done", "frames_match", "audio_duration", "resolution", "caption_timing", "caption_line_length", "silence"]
    assert all(c["ok"] for c in report["checks"])
    assert report["approx_ratio"] == 1.0
    assert load_story(project)["output"]["qc"] == "out/qc.json"


def test_stale_render_fails_frame_and_duration_checks(tmp_path):
    project = _rendered(tmp_path)
    story = load_story(project)
    story["lines"][0]["audio"]["duration_ms"] += 500
    save_story(project, story)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2
    assert "frames_match" in summary["failed"] and "audio_duration" in summary["failed"]


def test_overlapping_cues_fail_caption_timing(tmp_path):
    project = _rendered(tmp_path)
    ass = project / "out/captions.ass"
    # prepare_media durations [1000, 700, 1300] put L003 at 1950–3250 ms; pull its cue back over L001's
    ass.write_text(ass.read_text().replace("0:00:01.95,0:00:03.25", "0:00:00.50,0:00:03.25"), encoding="utf-8")
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2 and summary["failed"] == ["caption_timing"]
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_sf_qc.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sf_qc'`

- [ ] **Step 3: Implement `scripts/sf_qc.py`**

```python
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
    timeline = build_timeline(story)
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
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_sf_qc.py -v`
Expected: 3 passed

- [ ] **Step 5: Run the whole suite**

Run: `uv run pytest -q`
Expected: 68 passed

- [ ] **Step 6: Commit**

```bash
git add scripts/sf_qc.py tests/test_sf_qc.py
git commit -m "$(cat <<'EOF'
Add sf_qc: measure render against timeline, captions, and silences

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 13: Smoke production and end-to-end run

**Files:**
- Create: `projects/smoke-test/story.json`

**Interfaces:**
- Consumes: every script from Tasks 4–12 through their CLIs.

- [ ] **Step 1: Write `projects/smoke-test/story.json`**

A factual production (no canon) so it runs without a Story Skills project.

```json
{
  "schema_version": "1.0",
  "slug": "smoke-test",
  "canon": null,
  "brief": {
    "idea": "Why the sky is blue and sunsets are orange, in thirty seconds.",
    "language": "en",
    "aspect": "9:16",
    "content_type": "factual",
    "genre": "science-explainer",
    "target_seconds": 30,
    "captions": {"mode": "karaoke", "style": "karaoke-bold"},
    "review_mode": "gated"
  },
  "state": {"stage": "cast", "gates": {"script": {"approved_at": "2026-09-28"}, "images": {"approved_at": null}}},
  "style_bible": {
    "medium": "soft painterly digital illustration",
    "palette": ["sky blue", "warm orange", "deep navy"],
    "lighting": "natural daylight, golden hour for sunset scenes",
    "composition": "one clear subject, open sky, clean lower third for captions",
    "avoid": ["generated text", "logos", "watermarks", "photorealistic faces"]
  },
  "cast": [
    {
      "id": "narrator",
      "canon_id": null,
      "name": "Narrator",
      "role": "narrator",
      "voice": {"source": "design", "design_prompt": "male, middle-aged, low pitch, american accent", "profile_id": null},
      "caption_color": "#FFFFFF"
    },
    {
      "id": "C01",
      "canon_id": null,
      "name": "Kid",
      "role": "supporting",
      "appearance": "curious 9-year-old with a yellow raincoat and short curly hair",
      "voice": {"source": "design", "design_prompt": "female, child, high pitch, american accent", "profile_id": null},
      "caption_color": "#FFD166",
      "plates": {
        "face": {"prompt": "Soft painterly digital illustration, portrait of a curious 9-year-old with short curly hair and a yellow raincoat, neutral background, facing the viewer, no text, no logos.", "path": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null},
        "half": {"prompt": "Soft painterly digital illustration, half-body view of a curious 9-year-old with short curly hair in a yellow raincoat, hands in pockets, neutral background, no text, no logos.", "path": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null},
        "full": {"prompt": "Soft painterly digital illustration, full-body view of a curious 9-year-old with short curly hair in a yellow raincoat and rain boots, standing, neutral background, no text, no logos.", "path": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null}
      }
    }
  ],
  "locations": [
    {
      "id": "LOC01",
      "canon_id": null,
      "name": "Grassy hill",
      "appearance": "a gentle grassy hill under a wide open sky",
      "plate": {"prompt": "Soft painterly digital illustration, a gentle grassy hill under a wide open clear blue sky, no people, vertical composition, no text, no logos.", "path": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null}
    }
  ],
  "slides": [
    {
      "id": "S01",
      "source": null,
      "line_ids": ["L001", "L002"],
      "brief": {"moment": "The kid looks up at a bright blue sky", "characters": ["C01"], "location": "LOC01", "must_show": ["clear blue sky"], "must_not_show": ["sunset"], "continuity": ["yellow raincoat"], "beat": "question"},
      "visual": {"prompt": "Soft painterly digital illustration, a curious 9-year-old in a yellow raincoat standing on a grassy hill, looking up at a vast clear blue sky, wide shot, clean lower third, no text, no logos.", "shot": "wide", "motion": "push_in", "text_placement": "lower_third"},
      "image": {"path": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null, "seed": 101}
    },
    {
      "id": "S02",
      "source": null,
      "line_ids": ["L003"],
      "brief": {"moment": "White sunlight scatters off tiny air molecules", "characters": [], "location": null, "must_show": ["white light splitting into blue scatter"], "must_not_show": [], "continuity": [], "beat": "reveal"},
      "visual": {"prompt": "Soft painterly digital illustration, a beam of white sunlight entering the atmosphere and scattering blue light off tiny glowing air molecules, dark navy space above, clean lower third, no text, no labels, no logos.", "shot": "extreme-wide", "motion": "pan_right", "text_placement": "lower_third"},
      "image": {"path": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null, "seed": 102}
    },
    {
      "id": "S03",
      "source": null,
      "line_ids": ["L004"],
      "brief": {"moment": "Blue light reaches the kid's eyes from every direction", "characters": ["C01"], "location": "LOC01", "must_show": ["blue light from all directions"], "must_not_show": [], "continuity": ["yellow raincoat"], "beat": "reveal"},
      "visual": {"prompt": "Soft painterly digital illustration, a curious 9-year-old in a yellow raincoat on a grassy hill, soft blue light rays arriving from every direction of the sky toward the child, medium shot, clean lower third, no text, no logos.", "shot": "medium", "motion": "static", "text_placement": "lower_third"},
      "image": {"path": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null, "seed": 103}
    },
    {
      "id": "S04",
      "source": null,
      "line_ids": ["L005", "L006"],
      "brief": {"moment": "The same hill at sunset, glowing orange", "characters": ["C01"], "location": "LOC01", "must_show": ["orange sunset"], "must_not_show": [], "continuity": ["yellow raincoat"], "beat": "resolution"},
      "visual": {"prompt": "Soft painterly digital illustration, a curious 9-year-old in a yellow raincoat sitting on a grassy hill at sunset, warm orange and pink sky near a low sun, wide shot, clean lower third, no text, no logos.", "shot": "wide", "motion": "pull_out", "text_placement": "lower_third"},
      "image": {"path": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null, "seed": 104}
    }
  ],
  "lines": [
    {"id": "L001", "speaker": "narrator", "text": "Look up on a clear day, and the sky is blue. But sunlight is white.", "whisper": false, "pause_after_ms": 300, "claim_ids": ["CL01"], "audio": {"path": null, "duration_ms": null, "seed": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null, "qc": null, "asr_words": null}, "words": [], "words_hash": null},
    {"id": "L002", "speaker": "C01", "text": "So where does the blue come from?", "whisper": false, "pause_after_ms": 400, "claim_ids": [], "audio": {"path": null, "duration_ms": null, "seed": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null, "qc": null, "asr_words": null}, "words": [], "words_hash": null},
    {"id": "L003", "speaker": "narrator", "text": "Tiny molecules in the air scatter short blue wavelengths much more than long red ones.", "whisper": false, "pause_after_ms": 300, "claim_ids": ["CL02"], "audio": {"path": null, "duration_ms": null, "seed": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null, "qc": null, "asr_words": null}, "words": [], "words_hash": null},
    {"id": "L004", "speaker": "narrator", "text": "That scattered blue light reaches your eyes from every part of the sky. [pause 300ms] So the whole sky glows blue.", "whisper": false, "pause_after_ms": 400, "claim_ids": ["CL02"], "audio": {"path": null, "duration_ms": null, "seed": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null, "qc": null, "asr_words": null}, "words": [], "words_hash": null},
    {"id": "L005", "speaker": "C01", "text": "Then why are sunsets orange?", "whisper": false, "pause_after_ms": 300, "claim_ids": [], "audio": {"path": null, "duration_ms": null, "seed": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null, "qc": null, "asr_words": null}, "words": [], "words_hash": null},
    {"id": "L006", "speaker": "narrator", "text": "At sunset, light crosses much more air, so most of the blue is scattered away before it reaches you.", "whisper": false, "pause_after_ms": 500, "claim_ids": ["CL03"], "audio": {"path": null, "duration_ms": null, "seed": null, "input_hash": null, "status": "pending", "attempts": 0, "last_error": null, "qc": null, "asr_words": null}, "words": [], "words_hash": null}
  ],
  "research": {
    "notes": [
      {"id": "R01", "title": "Rayleigh scattering", "sources": ["https://en.wikipedia.org/wiki/Rayleigh_scattering"], "status": "verified", "accuracy": "must-be-accurate", "confidence": "high", "checked_on": "2026-09-28", "risk": []}
    ],
    "claims": [
      {"id": "CL01", "text": "Sunlight contains all visible wavelengths and appears white.", "status": "verified", "note_ids": ["R01"]},
      {"id": "CL02", "text": "Air molecules scatter shorter (blue) wavelengths much more strongly than longer (red) ones, which makes the daytime sky blue.", "status": "verified", "note_ids": ["R01"]},
      {"id": "CL03", "text": "At sunset sunlight travels through more atmosphere, so more blue is scattered out of the direct path and the sun and sky look orange-red.", "status": "verified", "note_ids": ["R01"]}
    ]
  },
  "source_work": null,
  "learnings_applied": [],
  "output": {"video": null, "captions": null, "contact_sheet": null, "qc": null}
}
```

- [ ] **Step 2: Validate it**

Run: `uv run scripts/sf_validate.py projects/smoke-test`
Expected: `{"ok": true, "errors": []}`

- [ ] **Step 3: Generate images with the fake provider and build the contact sheet**

Run: `uv run scripts/sf_image.py projects/smoke-test && uv run scripts/sf_contact_sheet.py projects/smoke-test`
Expected: first line `{"ok": true, "done": ["C01_face", "C01_half", "C01_full", "LOC01", "S01", "S02", "S03", "S04"], ...}`; second `{"ok": true, "tiles": 8, "missing": []}`. Open `projects/smoke-test/out/contact_sheet.png` and confirm 8 labeled tiles.

- [ ] **Step 4: Start VoiceStudio and synthesize voices**

Open the VoiceStudio app (it serves `http://localhost:3900`; the OmniVoice model and an ASR model such as WhisperX must be installed from its Model Catalogue). Then:

Run: `uv run scripts/sf_voice.py projects/smoke-test`
Expected: `{"ok": true, "profiles": ["narrator", "C01"], "done": ["L001", "L002", "L003", "L004", "L005", "L006"], ...}`. If a line lands in `needs_human`, read its `audio.last_error` in `story.json` and listen to `audio/<id>.wav`; rerun with `--only <id>`.

- [ ] **Step 5: Align, caption, render, QC**

Run:

```bash
uv run scripts/sf_align.py projects/smoke-test
uv run scripts/sf_captions.py projects/smoke-test
uv run scripts/sf_render.py projects/smoke-test
uv run scripts/sf_qc.py projects/smoke-test
```

Expected: each prints `"ok": true`. `sf_align` reports an `approx_ratio` well below 1.0 (real ASR timings). Play `projects/smoke-test/out/final.mp4`: six lines, two voices, karaoke highlight following the words, slide changes on the line boundaries of S01–S04.

- [ ] **Step 6: Record findings and commit**

If any step needed a fix, fix it in the owning script with a regression test first, then rerun from that step. Commit the smoke production (media is gitignored):

```bash
git add projects/smoke-test/story.json
git commit -m "$(cat <<'EOF'
Add smoke-test production for end-to-end engine runs

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
)"
```

Note: after the run, `story.json` holds real profile ids and hashes; commit it as-is or restore the pending version with `git checkout projects/smoke-test/story.json` before committing, whichever the user prefers (ask).
