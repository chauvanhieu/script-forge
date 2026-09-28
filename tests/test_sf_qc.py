import json

from fixtures import make_story, prepare_media
import sf_captions
import sf_qc
import sf_render
from sflib.project import ROOT, load_story, save_story

SMALL = (360, 640)
STYLES = ROOT / "config" / "caption-styles"


def _rendered(tmp_path):
    project = prepare_media(tmp_path, make_story(), [1000, 700, 1300])
    sf_captions.run(project, styles_dir=STYLES)
    sf_render.run(project, size=SMALL)
    return project


def test_clean_render_passes_every_check(tmp_path):
    project = _rendered(tmp_path)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 0, summary
    report = json.loads((project / "out/qc.json").read_text())
    assert [c["name"] for c in report["checks"]] == [
        "assets_done", "frames_match", "audio_duration", "resolution", "caption_timing", "caption_line_length", "silence"]
    assert all(c["ok"] for c in report["checks"])
    assert report["approx_ratio"] == 1.0
    assert load_story(project)["output"]["qc"] == "out/qc.json"


def test_stale_render_fails_frame_and_duration_checks(tmp_path):
    project = _rendered(tmp_path)
    story = load_story(project)
    story["lines"][0]["audio"]["duration_ms"] += 500
    save_story(project, story)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2
    assert "frames_match" in summary["failed"] and "audio_duration" in summary["failed"]


def test_overlapping_cues_fail_caption_timing(tmp_path):
    project = _rendered(tmp_path)
    ass = project / "out/captions.ass"
    # prepare_media durations [1000, 700, 1300] put L003 at 1950–3250 ms; pull its cue back over L001's
    ass.write_text(ass.read_text().replace("0:00:01.95,0:00:03.25", "0:00:00.50,0:00:03.25"), encoding="utf-8")
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2 and summary["failed"] == ["caption_timing"]


def test_missing_audio_fails_gracefully_without_a_timeline(tmp_path):
    project = prepare_media(tmp_path, make_story(), [1000, 700, 1300])
    story = load_story(project)
    story["lines"][0]["audio"]["status"] = "pending"
    story["lines"][0]["audio"]["duration_ms"] = None
    save_story(project, story)
    summary, code = sf_qc.run(project, size=SMALL, styles_dir=STYLES)
    assert code == 2
    assert "assets_done" in summary["failed"]
    report = json.loads((project / "out/qc.json").read_text())
    assert [c["name"] for c in report["checks"]] == [
        "assets_done", "frames_match", "audio_duration", "resolution", "caption_timing", "caption_line_length", "silence"]
    assert load_story(project)["output"]["qc"] == "out/qc.json"
