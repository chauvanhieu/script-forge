"""Thin wrappers around ffmpeg and ffprobe."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


def _probe(path: Path, args: list[str]) -> dict:
    proc = subprocess.run(["ffprobe", "-v", "error", *args, "-of", "json", str(path)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {path}: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def probe_duration_ms(path: Path) -> int:
    data = _probe(path, ["-show_entries", "format=duration"])
    return round(float(data["format"]["duration"]) * 1000)


def probe_video(path: Path) -> dict:
    data = _probe(path, ["-count_frames", "-select_streams", "v:0", "-show_entries", "stream=width,height,nb_read_frames"])
    stream = data["streams"][0]
    return {"width": int(stream["width"]), "height": int(stream["height"]), "frames": int(stream["nb_read_frames"])}


def probe_audio_ms(path: Path) -> int:
    data = _probe(path, ["-select_streams", "a:0", "-show_entries", "stream=duration"])
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
                           "-f", "s16le", "-ac", "1", "-ar", str(rate), "-"], capture_output=True, text=False)
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace") if isinstance(proc.stderr, bytes) else proc.stderr
        raise RuntimeError(f"ffmpeg decode failed on {path}: {stderr.strip()}")
    return proc.stdout


def silences(path: Path, noise_db: int = -45, min_s: float = 0.3) -> list[float]:
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af",
                           f"silencedetect=noise={noise_db}dB:d={min_s}", "-f", "null", "-"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg silence detection failed on {path}: {proc.stderr.strip()}")
    return [float(v) for v in re.findall(r"silence_duration: ([0-9.]+)", proc.stderr)]
