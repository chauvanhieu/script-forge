from fixtures import make_story
import sf_chapters
from sf_validate import reference_errors, schema_errors
from sflib.project import ROOT


def _chapter(n, texts_per_slide):
    return {"chapter": f"{n:02d}", "title": f"Chapter {n}",
            "slides": [{"moment": "m", "prompt": "a calm village", "shot": "wide", "motion": "push_in", "lines": t}
                       for t in texts_per_slide]}


def test_build_numbers_lines_slides_and_pauses():
    episode = {"style_suffix": "painterly", "brief": {"captions": {"mode": "none", "style": "karaoke-bold"}},
               "pause_ms": {"line": 700, "chapter_end": 1500, "final": 2500},
               "research": {"notes": [{"id": "R01", "title": "t", "sources": ["s"], "status": "verified"}], "claims": []}}
    chapters = [_chapter(0, [["One line.", "Two line."]]), _chapter(1, [["Three."], ["Four.", "Five numbers 5."]])]
    base = make_story()
    base["canon"] = None
    base["brief"]["content_type"] = "factual"
    story, index, problems = sf_chapters.build(base, episode, chapters)
    assert [s["line_ids"] for s in story["slides"]] == [["L001", "L002"], ["L003"], ["L004", "L005"]]
    assert [line["pause_after_ms"] for line in story["lines"]] == [700, 1500, 700, 700, 2500]
    assert story["slides"][0]["visual"]["prompt"] == "a calm village, painterly"
    assert index[1] == {"chapter": "01", "title": "Chapter 1", "first_line": "L003"}
    assert problems == ["L005: banned character in 'Five numbers 5.'"]
    assert schema_errors(story) == [] and reference_errors(story, ROOT) == []
