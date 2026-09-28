from fixtures import make_story, write_project
import sf_captions
from sflib.project import ROOT, load_story

STYLES = ROOT / "config" / "caption-styles"

WORDS = {
    "L001": [("Every", 0, 300), ("night", 300, 600), ("for", 600, 800), ("eleven", 800, 1200), ("years.", 1200, 1500)],
    "L002": [("Every", 0, 300), ("single", 300, 600), ("night.", 600, 900)],
    "L003": [("No.", 0, 400), ("Not", 600, 900), ("again.", 900, 1300)],
}
DURATIONS = {"L001": 1500, "L002": 900, "L003": 1300}


def _project(tmp_path, mode="karaoke", style="karaoke-bold"):
    story = make_story()
    story["brief"]["captions"] = {"mode": mode, "style": style}
    for line in story["lines"]:
        line["audio"].update(status="done", duration_ms=DURATIONS[line["id"]], input_hash=f"h-{line['id']}")
        line["words"] = [{"text": t, "start_ms": s, "end_ms": e, "approx": False} for t, s, e in WORDS[line["id"]]]
        line["words_hash"] = f"h-{line['id']}"
    return write_project(tmp_path, story)


def test_helpers():
    assert sf_captions.ass_color("#FFD166") == "&H0066D1FF"
    assert sf_captions.ass_time(1500) == "0:00:01.50"
    assert sf_captions.ass_time(3_723_450) == "1:02:03.45"


def test_karaoke_ass(tmp_path):
    project = _project(tmp_path)
    summary, code = sf_captions.run(project, styles_dir=STYLES)
    assert code == 0 and summary["cues"] == 3
    ass = (project / "out/captions.ass").read_text(encoding="utf-8")
    assert "PlayResX: 1080\nPlayResY: 1920" in ass
    assert "Style: narrator,Arial,78,&H00FFFFFF,&H009A9A9A,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,2,60,60,0,1" in ass
    assert "Style: C01,Arial,78,&H0066D1FF,&H009A9A9A," in ass
    assert ("Dialogue: 0,0:00:00.00,0:00:01.50,narrator,,0,0,422,,"
            "{\\an2}{\\kf30}Every {\\kf30}night {\\kf20}for\\N{\\kf40}eleven {\\kf30}years.") in ass
    assert "Dialogue: 0,0:00:02.65,0:00:03.95,C01,,0,0,422,,{\\an2}{\\kf60}No. {\\kf30}Not {\\kf40}again." in ass
    assert load_story(project)["output"]["captions"] == "out/captions.ass"


def test_plain_ass(tmp_path):
    project = _project(tmp_path, mode="plain", style="subtitle-clean")
    sf_captions.run(project, styles_dir=STYLES)
    ass = (project / "out/captions.ass").read_text(encoding="utf-8")
    assert "Dialogue: 0,0:00:00.00,0:00:01.50,narrator,,0,0,384,,{\\an2}Every night for\\Neleven years." in ass


def test_mode_none_writes_nothing(tmp_path):
    project = _project(tmp_path, mode="none")
    summary, code = sf_captions.run(project, styles_dir=STYLES)
    assert code == 0 and summary["cues"] == 0
    assert not (project / "out/captions.ass").exists()
    assert load_story(project)["output"]["captions"] is None


def test_stale_words_need_alignment(tmp_path):
    project = _project(tmp_path)
    story = load_story(project)
    story["lines"][1]["words_hash"] = "old"
    from sflib.project import save_story
    save_story(project, story)
    summary, code = sf_captions.run(project, styles_dir=STYLES)
    assert code == 2 and summary["needs_human"] == ["L002: words are missing or stale; run sf_align"]
