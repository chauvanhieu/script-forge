#!/usr/bin/env python3
"""Align script tokens to ASR word timings; captions always show script text."""
from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
from statistics import median

from sflib.media import silences
from sflib.project import EXIT_HUMAN, EXIT_OK, EXIT_PROVIDER, ProviderError, load_config, load_story, log, main_wrapper, save_story, wanted
from sflib.text import clusters, norm, tokens, uses_clusters
from sflib.voicestudio import VoiceStudio

MIN_MATCH_RATIO = 0.3
MIN_SPAN_RATIO = 0.6  # trimmed takes end on speech, so the last word should end near the audio's end
MIN_MEDIAN_MS_PER_CHAR = 25  # a collapsed aligner gives exactly one 20 ms frame per character; real speech is 30-45
MAX_ANCHOR_DRIFT_MS = 800  # how far a pause may sit from where the plain split expects a phrase break
PAUSE_NOISE_DB = -40
PAUSE_MIN_S = 0.15  # intra-line pauses are shorter than the between-line gaps sf_qc checks
PAUSE_EDGE_MS = 10  # silences touching the clip edges are trim leftovers, not pauses
PHRASE_END = set(",.!?…;:，。！？；：、")
CLOSERS = "\"'”’»)]」』）"


def timing_distrust(asr_words: list[dict], duration_ms: int) -> str | None:
    """Why these ASR word times can't be trusted for this audio, or None if they look plausible.

    VoiceStudio's forced aligner can collapse a line (e.g. its vi wav2vec2 model has no trained CTC head, so
    each character gets one 20 ms frame); such times are worse than the length-weighted fallback."""
    timed = [w for w in asr_words if w.get("start") is not None and w.get("end") is not None
             and w["end"] > w["start"] and norm(w["text"])]
    if not timed or not duration_ms:
        return None
    last_ms = round(max(w["end"] for w in timed) * 1000)
    if last_ms < MIN_SPAN_RATIO * duration_ms:
        return f"ASR words end at {last_ms} ms of {duration_ms} ms audio"
    per_char = median((w["end"] - w["start"]) * 1000 / len(norm(w["text"])) for w in timed)
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


def _ends_phrase(token: str) -> bool:
    stripped = token.rstrip(CLOSERS)
    return bool(stripped) and stripped[-1] in PHRASE_END


def _anchored_split(script_tokens: list[str], duration_ms: int, pauses_ms: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Length-weighted split whose phrase breaks snap onto the line's real pauses (unmatched pauses are ignored)."""
    plain = _split(script_tokens, 0, duration_ms)
    candidates = [i for i in range(1, len(script_tokens)) if _ends_phrase(script_tokens[i - 1])]
    anchors: list[tuple[int, int, int]] = []  # (first token after the break, pause start, pause end)
    for pause_start, pause_end in sorted(pauses_ms):
        if anchors and pause_start < anchors[-1][2]:
            continue

        def drift(index: int) -> int:
            expected = plain[index][0]
            return max(pause_start - expected, expected - pause_end, 0)

        usable = [i for i in candidates if not anchors or i > anchors[-1][0]]
        best = min(usable, key=drift, default=None)
        if best is not None and drift(best) <= MAX_ANCHOR_DRIFT_MS:
            anchors.append((best, pause_start, pause_end))
    spans, first, start = [], 0, 0
    for index, pause_start, pause_end in anchors:
        spans += _split(script_tokens[first:index], start, pause_start)
        first, start = index, pause_end
    return spans + _split(script_tokens[first:], start, duration_ms)


def line_pauses(wav: Path, duration_ms: int) -> list[tuple[int, int]]:
    """Internal silences (start_ms, end_ms) of a line's audio."""
    pauses = []
    for start_s, length_s in silences(wav, PAUSE_NOISE_DB, PAUSE_MIN_S):
        start, end = round(start_s * 1000), round((start_s + length_s) * 1000)
        if start > PAUSE_EDGE_MS and end < duration_ms - PAUSE_EDGE_MS:
            pauses.append((start, end))
    return pauses


def align_line(script_tokens: list[str], asr_words: list[dict], duration_ms: int, language: str,
               pauses_ms: list[tuple[int, int]] | None = None) -> list[dict]:
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
                start_val, end_val = unit.get("start"), unit.get("end")
                if start_val is not None and end_val is not None and keys[i1 + offset]:
                    times[i1 + offset] = (round(start_val * 1000), round(end_val * 1000))
    matched = sum(t is not None for t in times)
    approx = [t is None for t in times]
    if matched == 0 or matched < MIN_MATCH_RATIO * len(script_tokens):
        spans = _anchored_split(script_tokens, duration_ms, pauses_ms) if pauses_ms else _split(script_tokens, 0, duration_ms)
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
            left_span = spans[index - 1] if index > 0 else None
            left = left_span[1] if left_span is not None else 0
            right_span = spans[run_end] if run_end < len(spans) else None
            right = right_span[0] if right_span is not None else duration_ms
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
            if vs is not None:
                try:
                    asr_words = vs.transcribe_words(project_dir / audio["path"], language.split("-")[0])
                except ProviderError as exc:
                    if exc.code in ("quota", "auth"):
                        save_story(project_dir, story)
                        summary["errors"].append(f"{exc.code}: {exc.message}")
                        return summary, EXIT_PROVIDER
                    asr_words = []
            else:
                wav_path = project_dir / audio["path"]
                if wav_path.exists():
                    import mlx_whisper
                    log(project_dir, "sf_align", f"{line['id']}: extracting word timestamps via mlx_whisper cross-attention")
                    try:
                        result = mlx_whisper.transcribe(
                            str(wav_path),
                            word_timestamps=True,
                            initial_prompt=line["text"],
                            language=language.split("-")[0]
                        )
                        asr_words = []
                        for segment in result.get("segments", []):
                            for word in segment.get("words", []):
                                if word.get("word") and word.get("start") is not None and word.get("end") is not None:
                                    asr_words.append({
                                        "text": word["word"].strip(),
                                        "start": word["start"],
                                        "end": word["end"]
                                    })
                    except Exception as exc:
                        log(project_dir, "sf_align", f"{line['id']}: mlx_whisper failed: {exc}")
                        asr_words = []
                else:
                    asr_words = []
        reason = timing_distrust(asr_words, audio["duration_ms"])
        if reason:
            asr_words = []
            summary["untrusted_timings"].append(f"{line['id']}: {reason}")
            log(project_dir, "sf_align", f"{line['id']}: discarded ASR word times ({reason}); using approx split")
        wav = project_dir / audio["path"]
        pauses = line_pauses(wav, audio["duration_ms"]) if wav.exists() else None  # only used if the split is approx
        line["words"] = align_line(tokens(line["text"], language), asr_words, audio["duration_ms"], language, pauses)
        line["words_hash"] = audio["input_hash"]
        summary["aligned"].append(line["id"])
    save_story(project_dir, story)
    all_words = [word for line in story["lines"] for word in line.get("words") or []]
    if all_words:
        summary["approx_ratio"] = round(sum(word["approx"] for word in all_words) / len(all_words), 3)
    return summary, EXIT_HUMAN if summary["needs_human"] else EXIT_OK


if __name__ == "__main__":
    main_wrapper(run, __doc__)
