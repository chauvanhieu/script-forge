import wave

from fixtures import padded_tone_wav_bytes, silence_wav_bytes
from sflib.media import trim_silence

RATE = 24000


def _write(path, data: bytes) -> None:
    path.write_bytes(data)


def _frame_count(path) -> int:
    with wave.open(str(path), "rb") as wav:
        return wav.getnframes()


def test_trim_silence_keeps_pad_around_the_loud_span(tmp_path):
    wav_path = tmp_path / "take.wav"
    _write(wav_path, padded_tone_wav_bytes(300, 500, 300, rate=RATE))
    trim_silence(wav_path, pad_ms=50)
    expected = round(RATE * (50 + 500 + 50) / 1000)
    assert abs(_frame_count(wav_path) - expected) <= 1


def test_trim_silence_leaves_an_all_silent_file_unchanged(tmp_path):
    wav_path = tmp_path / "silent.wav"
    data = silence_wav_bytes(400, rate=RATE)
    _write(wav_path, data)
    trim_silence(wav_path, pad_ms=50)
    assert wav_path.read_bytes() == data


def test_trim_silence_never_extends_beyond_the_file(tmp_path):
    # loud audio starts 20ms in, well under the 50ms pad -> clamp to frame 0
    wav_path = tmp_path / "take.wav"
    _write(wav_path, padded_tone_wav_bytes(20, 200, 20, rate=RATE))
    trim_silence(wav_path, pad_ms=50)
    expected = round(RATE * (20 + 200 + 20) / 1000)
    assert abs(_frame_count(wav_path) - expected) <= 1


def test_trim_silence_rejects_non_16_bit_pcm(tmp_path):
    wav_path = tmp_path / "eightbit.wav"
    with wave.open(str(wav_path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(1)
        wav.setframerate(RATE)
        wav.writeframes(b"\x80" * 100)
    try:
        trim_silence(wav_path)
        assert False, "expected RuntimeError"
    except RuntimeError as exc:
        assert "16-bit" in str(exc)
