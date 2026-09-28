import pytest

from fixtures import make_story
from sflib.timeline import build_timeline


def _with_durations(story, durations):
    for line, ms in zip(story["lines"], durations):
        line["audio"]["duration_ms"] = ms
    return story


def test_line_and_slide_spans_follow_measured_durations_and_pauses():
    tl = build_timeline(_with_durations(make_story(), [1000, 700, 1300]))
    assert tl.line_start_ms == {"L001": 0, "L002": 1250, "L003": 1950}
    assert tl.line_end_ms == {"L001": 1000, "L002": 1950, "L003": 3250}
    assert tl.total_ms == 3650
    s1, s2 = tl.slides
    assert (s1.slide_id, s1.start_ms, s1.end_ms) == ("S01", 0, 1950)
    assert (s2.slide_id, s2.start_ms, s2.end_ms) == ("S02", 1950, 3650)


def test_slide_frames_tile_the_whole_timeline_without_drift():
    tl = build_timeline(_with_durations(make_story(), [1000, 700, 1300]))
    assert tl.slides[0].end_frame == tl.slides[1].start_frame
    assert sum(s.frames for s in tl.slides) == tl.total_frames == 110


def test_missing_duration_raises():
    with pytest.raises(ValueError, match="L001"):
        build_timeline(make_story())
