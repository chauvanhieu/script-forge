#!/usr/bin/env python3
"""StoryForge image command (spec 8.2) backed by FLUX.2-klein-4B running locally through mflux (MLX).

  generate.py --prompt-file p.txt --aspect 9:16 [--ref a.png ...] [--seed n] --out S07.png

Success: exit 0 and a PNG at --out. Failure: exit 1 and a last stderr line
{"error": "invalid|auth|transient|...", "message": "..."}.
References are passed to FLUX.2's multi-image edit conditioning, so slides see the plates.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import zlib
from pathlib import Path

MODEL = "flux2-klein-4b"
QUANTIZE = int(os.environ.get("SF_LOCAL_IMAGE_QUANTIZE", "8"))  # 4 = smaller/faster, 8 = closer to bf16
STEPS = int(os.environ.get("SF_LOCAL_IMAGE_STEPS", "4"))        # klein is distilled for 4 steps
# Refs are encoded at their own size; 512px keeps identity and cuts a 2-ref slide from ~65s to ~26s.
REF_PX = int(os.environ.get("SF_LOCAL_IMAGE_REF_PX", "512"))
# Exact engine aspect ratios, multiples of 16 (FLUX latent grid), ~1 MP.
SIZES = {"1:1": (1024, 1024), "3:4": (768, 1024), "9:16": (720, 1280), "16:9": (1280, 720)}


class Failure(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class _Parser(argparse.ArgumentParser):
    def error(self, message: str):  # argparse would exit 2 with plain text; the contract wants JSON
        raise Failure("invalid", message)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = _Parser(description=__doc__)
    parser.add_argument("--prompt-file", type=Path, required=True)
    parser.add_argument("--aspect", required=True, choices=sorted(SIZES))
    parser.add_argument("--ref", type=Path, action="append", default=[])
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        args.prompt = args.prompt_file.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError as exc:
        raise Failure("invalid", f"prompt file is not valid UTF-8: {args.prompt_file}: {exc}") from exc
    except OSError as exc:
        raise Failure("invalid", f"cannot read prompt file: {exc}") from exc
    if not args.prompt:
        raise Failure("invalid", "prompt file is empty")
    from PIL import Image

    for ref in args.ref:
        if not ref.is_file():
            raise Failure("invalid", f"reference image not found: {ref}")
        try:
            with Image.open(ref) as image:
                image.verify()
        except Exception as exc:  # any decoder failure means the ref is unusable input
            raise Failure("invalid", f"reference image is not a decodable image: {ref}: {exc}") from exc
    if args.seed is None:  # deterministic per prompt so reruns reproduce the same plate
        args.seed = zlib.crc32(args.prompt.encode("utf-8"))
    return args


def classify(exc: BaseException) -> Failure:
    """Map an unexpected exception to a contract error code.

    Only the wrapper's own input checks (parse_args) produce "invalid"; sf_image stops the whole batch on it.
    Anything unexpected is "transient": sf_image retries, then marks just that item needs_human.
    """
    text = f"{type(exc).__name__}: {exc}"[-500:]
    try:
        from huggingface_hub.errors import HfHubHTTPError, LocalEntryNotFoundError, RepositoryNotFoundError
    except ImportError:
        return Failure("transient", text)
    status = getattr(getattr(exc, "response", None), "status_code", None)
    # RepositoryNotFoundError covers GatedRepoError; LocalEntryNotFoundError = offline with no cached weights.
    if isinstance(exc, (RepositoryNotFoundError, LocalEntryNotFoundError)) or (
            isinstance(exc, HfHubHTTPError) and status in (401, 403)):
        return Failure("auth", f"model weights unavailable (setup problem): {text}")
    return Failure("transient", text)  # OOM, Metal errors, network hiccups, library bugs


def shrink_refs(refs: list[Path], tmp: Path) -> list[str]:
    from PIL import Image

    paths = []
    for index, ref in enumerate(refs):
        with Image.open(ref) as image:
            image = image.convert("RGB")
            image.thumbnail((REF_PX, REF_PX))
            path = tmp / f"ref{index}.png"
            image.save(path)
        paths.append(str(path))
    return paths


def generate(args: argparse.Namespace) -> None:
    from mflux.models.common.config import ModelConfig
    from mflux.models.flux2.variants import Flux2Klein, Flux2KleinEdit

    width, height = SIZES[args.aspect]
    common = dict(seed=args.seed, prompt=args.prompt, num_inference_steps=STEPS, width=width, height=height)
    config = ModelConfig.from_name(MODEL)
    started = time.monotonic()
    if args.ref:  # the edit variant requires at least one reference image
        model = Flux2KleinEdit(quantize=QUANTIZE, model_config=config)
        loaded = time.monotonic()
        with tempfile.TemporaryDirectory() as tmp:
            image = model.generate_image(**common, image_paths=shrink_refs(args.ref, Path(tmp)))
    else:
        model = Flux2Klein(quantize=QUANTIZE, model_config=config)
        loaded = time.monotonic()
        image = model.generate_image(**common)
    done = time.monotonic()
    sys.stderr.write(f"local-image: load {loaded - started:.1f}s, generate {done - loaded:.1f}s, "
                     f"{width}x{height}, seed {args.seed}, refs {len(args.ref)}\n")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.out.with_suffix(".tmp.png")
    image.image.save(tmp, format="PNG")
    tmp.replace(args.out)  # never leave a half-written PNG at --out


def main(argv: list[str]) -> int:
    try:
        generate(parse_args(argv))
    except Exception as exc:  # the last stderr line must always be the contract JSON
        failure = exc if isinstance(exc, Failure) else classify(exc)
        sys.stderr.write(json.dumps({"error": failure.code, "message": str(failure)}) + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
