"""Shared project IO for StoryForge scripts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import traceback
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
    except Exception as exc:
        if args.project_dir.is_dir():
            log(args.project_dir, Path(sys.argv[0]).stem, traceback.format_exc())
        else:
            sys.stderr.write(traceback.format_exc())
        _emit({"errors": [f"{type(exc).__name__}: {exc}"]}, EXIT_BUG)
    _emit(summary, code)
