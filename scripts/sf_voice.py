#!/usr/bin/env python3
"""Create voice profiles and synthesize every line through VoiceStudio, with transcribe-back QC."""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Callable

from sflib.media import probe_duration_ms, trim_silence
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


def _ensure_profiles(story: dict, vs, root: Path, project_dir: Path, summary: dict, recast: set[str]) -> None:
    language = story["brief"]["language"].split("-")[0]
    for member in story["cast"]:
        voice = member["voice"]
        if voice.get("profile_id") and member["id"] not in recast:
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
            ref_text = next((shown for line in story["lines"] if line["speaker"] == member["id"]
                             and (shown := display_text(line["text"]))), "")
            voice["profile_id"] = vs.create_design_profile(name, parsed.get("attrs", {}), voice["instruct"], language,
                                                            ref_text)
        else:
            ref_audio = root / voice["ref_audio"]
            if not ref_audio.is_file():
                summary["needs_human"].append(f"{member['id']}: reference audio {ref_audio} is missing")
                continue
            voice["profile_id"] = vs.create_clone_profile(name, ref_audio, voice.get("ref_text", ""), language)
            voice["instruct"] = ""
        summary["profiles"].append(member["id"])
        save_story(project_dir, story)


def _quality(vs, wav: Path, line: dict, language: str, duration_ms: int, meta: dict, qc_cfg: dict) -> tuple[dict, list | None]:
    shown = display_text(line["text"])
    qc: dict = {"cps": None, "cer": None, "asr": "ok", "reasons": []}
    if meta.get("dropped_chunks"):
        qc["reasons"].append("VoiceStudio dropped part of the text")
    if shown:  # a tag-only line (e.g. "[sigh]") has nothing to clock a speaking rate against
        cps = len("".join(norm(shown).split())) / max(duration_ms / 1000, 0.001)
        qc["cps"] = round(cps, 2)
        if not qc_cfg["min_cps"] <= cps <= qc_cfg["max_cps"]:
            qc["reasons"].append(f"speaking rate {cps:.1f} chars/s outside [{qc_cfg['min_cps']}, {qc_cfg['max_cps']}]")
    words = None
    try:
        words = vs.transcribe_words(wav, language)
    except ProviderError as exc:
        qc["asr"] = f"skipped: {exc.code}: {exc.message}"
    if words is not None and shown:  # an empty reference makes CER meaningless (0 or 1 on ASR noise alone)
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
    recast = set(cast) & (only or set())  # --only C01 re-creates C01's profile and re-voices all its lines
    try:
        vs.health()
        _ensure_profiles(story, vs, root, project_dir, summary, recast)
        for line in story["lines"]:
            if not (wanted(line["id"], only) or line["speaker"] in recast):
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
            take_wav = wav.with_suffix(".take.wav")  # the old take stays in place until this line is finished
            try:
                for take in range(MAX_RETAKES + 1):
                    seed = (base_seed + take * RETAKE_SEED_STEP) % 2_147_483_647
                    data, meta = _with_retries(lambda: vs.generate(text=line["text"], language=language, profile_id=profile_id,
                                                                    seed=seed, engine=engine, instruct=instruct), sleep)
                    take_wav.write_bytes(data)
                    trim_silence(take_wav)  # cut VoiceStudio's lead/trail padding so pause_after_ms is the audible gap
                    duration = probe_duration_ms(take_wav)
                    qc, words = _quality(vs, take_wav, line, language, duration, meta, voice_cfg["qc"])
                    audio["attempts"] = audio.get("attempts", 0) + 1
                    if not qc["reasons"]:
                        break
                os.replace(take_wav, wav)
            finally:
                take_wav.unlink(missing_ok=True)
            passed = not qc["reasons"]
            line["words"], line["words_hash"] = [], None  # new audio: sf_align must re-time this line
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
