import json

import pytest

from fixtures import make_story, prepare_media
import sf_captions
import sf_render
from sflib.media import probe_audio_ms, probe_video
from sflib.project import ROOT, load_story
from sflib.timeline import FPS, build_timeline

SMALL = (360, 640)


def test_motion_filter_expressions():
    vf = sf_render.motion_filter("push_in", 60, 360, 640)
    assert vf.startswith("scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,")
    assert "zoompan=z='1+0.08*on/60'" in vf and ":d=60:s=360x640:fps=30" in vf
    assert "x='(iw-iw/zoom)*on/60'" in sf_render.motion_filter("pan_right", 60, 360, 640)
    with pytest.raises(ValueError):
        sf_render.motion_filter("spin", 60, 360, 640)


def test_render_matches_the_timeline_and_caches_clips(tmp_path):
    story = make_story()
    story["brief"]["captions"]["mode"] = "none"
    project = prepare_media(tmp_path, story, [1000, 700, 1300])
    summary, code = sf_render.run(project, size=SMALL)
    assert code == 0 and summary["rendered"] == ["S01", "S02"]
    timeline = build_timeline(load_story(project))
    video = probe_video(project / "out/final.mp4")
    assert (video["width"], video["height"]) == SMALL
    assert video["frames"] == timeline.total_frames == summary["frames"]
    assert abs(probe_audio_ms(project / "out/final.mp4") - timeline.total_ms) <= round(1000 / FPS)  # spec §8.4: ±1 frame
    assert load_story(project)["output"]["video"] == "out/final.mp4"
    summary, _ = sf_render.run(project, size=SMALL)
    assert summary["rendered"] == [] and summary["cached"] == 2


def test_render_burns_captions(tmp_path):
    project = prepare_media(tmp_path, make_story(), [1000, 700, 1300])
    sf_captions.run(project, styles_dir=ROOT / "config" / "caption-styles")
    summary, code = sf_render.run(project, size=SMALL)
    assert code == 0
    assert probe_video(project / "out/final.mp4")["frames"] == summary["frames"]


def test_missing_assets_need_human(tmp_path):
    project = prepare_media(tmp_path, make_story(), [1000, 700, 1300])
    (project / "images/S02.png").unlink()
    summary, code = sf_render.run(project, size=SMALL)
    assert code == 2
    assert summary["needs_human"] == ["S02: image missing", "captions are not built; run sf_captions"]


def test_corrupt_clip_manifest_is_rebuilt(tmp_path):
    story = make_story()
    story["brief"]["captions"]["mode"] = "none"
    project = prepare_media(tmp_path, story, [1000, 700, 1300])
    sf_render.run(project, size=SMALL)
    (project / "clips/manifest.json").write_text("{not json")
    summary, code = sf_render.run(project, size=SMALL)
    assert code == 0 and summary["rendered"] == ["S01", "S02"]
    assert set(json.loads((project / "clips/manifest.json").read_text())) == {"S01", "S02"}
    assert [p.name for p in (project / "clips").iterdir() if p.name.endswith(".tmp")] == []


def test_render_with_seo_title_and_metadata(tmp_path):
    import subprocess
    story = make_story()
    story["slug"] = "20261002-120000-legal-loophole"
    story["brief"]["captions"]["mode"] = "none"
    story["seo"] = {
        "title": "The Shocking Legal Loophole That Broke The System",
        "description": "An institutional court trial where justice divided the public.",
        "keywords": ["legal paradox", "court case", "shorts"],
        "author": "The Grey Verdict"
    }
    project = prepare_media(tmp_path, story, [1000, 700, 1300])
    summary, code = sf_render.run(project, size=SMALL)
    assert code == 0

    expected_file = "out/legal-loophole.mp4"
    assert summary["video"] == expected_file
    assert (project / expected_file).is_file()
    assert not (project / "out/final.mp4").exists()

    # Probe embedded metadata tags with ffprobe
    res = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries", "format_tags", "-of", "json",
        str(project / expected_file)
    ], capture_output=True, text=True, check=True)
    probe = json.loads(res.stdout)
    tags = probe.get("format", {}).get("tags", {})
    assert tags.get("title") == "The Shocking Legal Loophole That Broke The System"
    assert tags.get("artist") == "The Grey Verdict"
    assert "legal paradox" in tags.get("comment", "") or "legal paradox" in tags.get("description", "") or "legal paradox" in tags.get("keywords", "")


def test_render_with_sound_design_mixing(tmp_path):
    story = make_story()
    story["brief"]["captions"]["mode"] = "none"
    project = prepare_media(tmp_path, story, [1000, 700, 1300])

    # Add custom audio assets in project/audio
    audio_dir = project / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    import wave, struct
    for name in ["bgm_track.wav", "sfx_whoosh.wav"]:
        with wave.open(str(audio_dir / name), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(48000)
            # 0.5s of low tone
            raw = bytearray()
            for i in range(24000):
                raw.extend(struct.pack("<h", int(1000 * ((i % 100) / 100.0))))
            w.writeframes(raw)

    summary, code = sf_render.run(project, size=SMALL)
    assert code == 0
    assert "bgm" in summary.get("audio_design", [])
    assert "whoosh" not in summary.get("audio_design", [])
    timeline = build_timeline(load_story(project))
    assert abs(probe_audio_ms(project / summary["video"]) - timeline.total_ms) <= round(1000 / FPS)

