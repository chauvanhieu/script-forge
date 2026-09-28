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


def test_transcribe_words_reads_verbose_json_words(tmp_path):
    wav = tmp_path / "a.wav"
    wav.write_bytes(sine_wav_bytes(300))

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/audio/transcriptions"
        assert b'name="response_format"' in request.content and b"verbose_json" in request.content
        assert b'name="timestamp_granularities[]"' in request.content and b"word" in request.content
        return httpx.Response(200, json={"text": "Every night for", "words": [
            {"word": " Every", "start": 0.0, "end": 0.3},
            {"word": "night", "start": 0.3, "end": 0.6},
            {"word": " ", "start": 0.6, "end": 0.7},
            {"word": "for", "start": 0.7, "end": 0.9},
        ]})

    words = _client(handler).transcribe_words(wav, "en")
    assert words == [
        {"text": "Every", "start": 0.0, "end": 0.3},
        {"text": "night", "start": 0.3, "end": 0.6},
        {"text": "for", "start": 0.7, "end": 0.9},
    ]


def test_transcribe_words_handles_missing_words_key(tmp_path):
    wav = tmp_path / "a.wav"
    wav.write_bytes(sine_wav_bytes(100))

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/audio/transcriptions"
        return httpx.Response(200, json={"text": "something"})

    words = _client(handler).transcribe_words(wav, "en")
    assert words == []


def test_probe_duration_ms_raises_on_invalid_file(tmp_path):
    from sflib.media import probe_duration_ms
    bad_file = tmp_path / "x.wav"
    bad_file.write_text("not media")
    with pytest.raises(RuntimeError) as exc_info:
        probe_duration_ms(bad_file)
    assert "ffprobe failed" in str(exc_info.value)
    assert "x.wav" in str(exc_info.value)


def test_silences_raises_on_invalid_file(tmp_path):
    from sflib.media import silences
    bad_file = tmp_path / "x.wav"
    bad_file.write_text("not media")
    with pytest.raises(RuntimeError) as exc_info:
        silences(bad_file)
    assert "ffmpeg silence detection failed" in str(exc_info.value)
    assert "x.wav" in str(exc_info.value)
