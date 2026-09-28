from fixtures import FakeVS, make_story, write_project
import sf_align
import sf_captions
import sf_image
import sf_qc
import sf_render
import sf_voice
from sflib.project import ROOT, load_story, save_story

SMALL = (360, 640)
STYLES = ROOT / "config" / "caption-styles"
VOICE_CONFIG = {"voice": {"base_url": "http://vs.local", "engine": None, "qc": {"max_cer": 0.25, "min_cps": 2, "max_cps": 30}}}
L001_TEXT = "Every night for eleven years."


def _chain(project, root, vs):
    assert sf_voice.run(project, config=VOICE_CONFIG, client=vs, root=root)[1] == 0
    assert sf_align.run(project)[1] == 0
    assert sf_captions.run(project, styles_dir=STYLES)[1] == 0
    assert sf_render.run(project, size=SMALL)[1] == 0
    return sf_qc.run(project, size=SMALL, styles_dir=STYLES)


def test_revoiced_line_rebuilds_words_and_captions(tmp_path):
    project = write_project(tmp_path, make_story())
    sf_image.run(project, config={"image": {"provider": "fake", "max_refs": 4}})
    summary, code = _chain(project, tmp_path, FakeVS())
    assert code == 0, summary
    assert load_story(project)["lines"][0]["words"][-1]["end_ms"] == 1000

    story = load_story(project)
    story["lines"][0]["audio"]["status"] = "pending"  # /story-redo L001
    save_story(project, story)
    summary, code = _chain(project, tmp_path, FakeVS(durations={L001_TEXT: 2500}))
    assert code == 0, summary

    line = load_story(project)["lines"][0]
    assert line["audio"]["duration_ms"] == 2500
    assert line["words"][-1]["end_ms"] == 2500
    ass = (project / "out/captions.ass").read_text(encoding="utf-8")
    assert "Dialogue: 0,0:00:00.00,0:00:02.50,narrator," in ass
