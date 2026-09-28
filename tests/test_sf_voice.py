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
