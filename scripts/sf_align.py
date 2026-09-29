#!/usr/bin/env python3
"""Align script tokens to ASR word timings; captions always show script text."""
from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
from statistics import median

from sflib.project import EXIT_HUMAN, EXIT_OK, EXIT_PROVIDER, ProviderError, load_config, load_story, log, main_wrapper, save_story, wanted
from sflib.text import clusters, norm, tokens, uses_clusters
from sflib.voicestudio import VoiceStudio

MIN_MATCH_RATIO = 0.3
MIN_SPAN_RATIO = 0.6  # trimmed takes end on speech, so the last word should end near the audio's end
MIN_MEDIAN_MS_PER_CHAR = 25  # a collapsed aligner gives exactly one 20 ms frame per character; real speech is 30-45


def timing_distrust(asr_words: list[dict], duration_ms: int) -> str | None:
    """Why these ASR word times can't be trusted for this audio, or None if they look plausible.

    VoiceStudio's forced aligner can collapse a line (e.g. its vi wav2vec2 model has no trained CTC head, so
    each character gets one 20 ms frame); such times are worse than the length-weighted fallback."""
    timed = [w for w in asr_words if w.get("start") is not None and w.get("end") is not None]
    if not timed or not duration_ms:
        return None
    last_ms = round(max(w["end"] for w in timed) * 1000)
    if last_ms < MIN_SPAN_RATIO * duration_ms:
        return f"ASR words end at {last_ms} ms of {duration_ms} ms audio"
    per_char = median((w["end"] - w["start"]) * 1000 / max(1, len(w["text"])) for w in timed)
    if per_char < MIN_MEDIAN_MS_PER_CHAR:
        return f"ASR words last a median {per_char:.1f} ms per character (< {MIN_MEDIAN_MS_PER_CHAR})"
    return None


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
    summary: dict = {"aligned": [], "skipped": 0, "needs_human": [], "errors": [], "approx_ratio": 0.0,
                     "untrusted_timings": []}
    vs = client
    for line in story["lines"]:
        if not wanted(line["id"], only):
            continue
        audio = line["audio"]
        if audio.get("status") != "done" or not audio.get("duration_ms"):
            summary["needs_human"].append(f"{line['id']} has no audio")
            continue
        if only is None and line.get("words_hash") == audio["input_hash"]:  # a tag-only line aligns to []
            summary["skipped"] += 1
            continue
        asr_words = audio.get("asr_words")
        if asr_words is None:
            if vs is None:
                vs = VoiceStudio((config or load_config())["voice"]["base_url"])
            try:
                asr_words = vs.transcribe_words(project_dir / audio["path"], language.split("-")[0])
            except ProviderError as exc:
                if exc.code in ("quota", "auth"):
                    save_story(project_dir, story)
                    summary["errors"].append(f"{exc.code}: {exc.message}")
                    return summary, EXIT_PROVIDER
                asr_words = []
        reason = timing_distrust(asr_words, audio["duration_ms"])
        if reason:
            asr_words = []
            summary["untrusted_timings"].append(f"{line['id']}: {reason}")
            log(project_dir, "sf_align", f"{line['id']}: discarded ASR word times ({reason}); using approx split")
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
