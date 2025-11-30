import pytest

from segmenter import Line, build_segments


def test_line_assigned_to_segment_with_greater_overlap():
    lines = [
        {"start": 27.0, "end": 34.0, "text": "bridging line"},
    ]

    segments = build_segments(lines, segment_length=30.0)

    assert len(segments) == 2
    assert segments[0].lines == []
    assert [line.text for line in segments[1].lines] == ["bridging line"]


def test_midpoint_breaks_ties():
    lines = [
        {"start": 10.0, "end": 20.0, "text": "midpoint on boundary"},
    ]

    segments = build_segments(lines, segment_length=10.0)

    # Overlap is equal between segments 1 (10-20s) and 0 (0-10s) is zero; between
    # segment 1 and 2 (20-30s) is also zero. The midpoint is 15s, so the line
    # should go to segment 1.
    assert [line.text for line in segments[1].lines] == ["midpoint on boundary"]


def test_multiple_lines_keep_order_inside_segment():
    lines = [
        {"start": 5.0, "end": 8.0, "text": "early"},
        {"start": 12.0, "end": 18.0, "text": "later"},
        {"start": 28.0, "end": 32.0, "text": "cross"},
    ]

    segments = build_segments(lines, segment_length=20.0)

    assert [line.text for line in segments[0].lines] == ["early", "later"]
    assert [line.text for line in segments[1].lines] == ["cross"]
    assert segments[0].text == "early later"
    assert segments[1].text == "cross"


def test_total_duration_extends_segments_when_provided():
    lines = [{"start": 1.0, "end": 2.0, "text": "a"}]

    segments = build_segments(lines, segment_length=30.0, total_duration=75.0)

    assert len(segments) == 3
    assert segments[-1].start == 60.0
    assert segments[-1].end == 90.0


def test_empty_input_returns_empty_list():
    assert build_segments([], segment_length=30.0) == []
