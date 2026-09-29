"""Contract self-check that needs no model: uv run --project tools/local-image python tools/local-image/test_generate.py"""
import contextlib
import io
import json
import tempfile
from pathlib import Path

import generate


def run(argv: list[str]) -> tuple[int, dict | None]:
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        code = generate.main(argv)
    lines = err.getvalue().strip().splitlines()
    return code, json.loads(lines[-1]) if lines else None


with tempfile.TemporaryDirectory() as tmp:
    prompt = Path(tmp, "p.txt")
    prompt.write_text("a hill", encoding="utf-8")
    out = str(Path(tmp, "o.png"))
    assert run(["--prompt-file", str(prompt), "--aspect", "2:1", "--out", out])[1]["error"] == "invalid"
    assert run(["--prompt-file", str(Path(tmp, "nope.txt")), "--aspect", "1:1", "--out", out])[1]["error"] == "invalid"
    assert run(["--prompt-file", str(prompt), "--aspect", "1:1", "--ref", "missing.png", "--out", out])[1]["error"] == "invalid"
    assert run(["--aspect", "1:1"])[0] == 1
    bad_utf8 = Path(tmp, "bad.txt")
    bad_utf8.write_bytes(b"a hill \xff\xfe")
    code, err = run(["--prompt-file", str(bad_utf8), "--aspect", "1:1", "--out", out])
    assert code == 1 and err["error"] == "invalid" and "UTF-8" in err["message"], err
    not_png = Path(tmp, "ref.png")
    not_png.write_text("not an image")
    assert run(["--prompt-file", str(prompt), "--aspect", "1:1", "--ref", str(not_png), "--out", out])[1]["error"] == "invalid"

    def boom(args):
        raise ValueError("deep mflux/numpy failure")
    real_generate, generate.generate = generate.generate, boom
    code, err = run(["--prompt-file", str(prompt), "--aspect", "1:1", "--out", out])
    generate.generate = real_generate
    assert code == 1 and err["error"] == "transient" and "ValueError" in err["message"], err
    args = generate.parse_args(["--prompt-file", str(prompt), "--aspect", "9:16", "--out", out])
    assert args.seed == generate.parse_args(["--prompt-file", str(prompt), "--aspect", "9:16", "--out", out]).seed

for aspect, (w, h) in generate.SIZES.items():
    a, b = map(int, aspect.split(":"))
    assert w * b == h * a and w % 16 == 0 and h % 16 == 0, aspect

import httpx
from huggingface_hub.errors import GatedRepoError, HfHubHTTPError, LocalEntryNotFoundError

def http_error(cls, status):
    request = httpx.Request("GET", "https://huggingface.co/x")
    return cls("hf", response=httpx.Response(status, request=request))

assert generate.classify(http_error(GatedRepoError, 403)).code == "auth"
assert generate.classify(http_error(HfHubHTTPError, 401)).code == "auth"
assert generate.classify(http_error(HfHubHTTPError, 503)).code == "transient"
assert generate.classify(LocalEntryNotFoundError("offline, not cached")).code == "auth"
assert generate.classify(RuntimeError("HTTP 401 in some unrelated text")).code == "transient"
for exc in (TypeError("x"), ValueError("x"), AttributeError("x"), KeyError("x"), ImportError("x")):
    assert generate.classify(exc).code == "transient", exc
assert generate.classify(RuntimeError("[metal] out of memory")).code == "transient"
print("ok")
