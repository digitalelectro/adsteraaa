"""
Utilities for assigning timestamped lines of a script to fixed-length segments.

The key behavior matches the described production workflow:
- Each line has a start and end timestamp from the recorded narration.
- Segments are fixed length (e.g., 30 seconds).
- If a line spans a boundary, it should belong to the segment where it has the
  greatest time coverage. The line is kept intact in that segment and removed
  from the other.

Typical usage:
    lines = [
        {"start": 27.0, "end": 34.0, "text": "crucial line"},
        {"start": 34.0, "end": 55.0, "text": "next"},
    ]
    segments = build_segments(lines, segment_length=30.0)

The resulting manifest assigns the first line entirely to the 30–60 second
segment because it spends more time there.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import Iterable, List, Sequence


@dataclass
class Line:
    """A timestamped line from the narration transcript."""

    start: float
    end: float
    text: str

    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass
class Segment:
    """A fixed-length container for lines assigned by time coverage."""

    index: int
    start: float
    end: float
    lines: List[Line] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(line.text.strip() for line in self.lines if line.text.strip())


def _compute_overlap(start_a: float, end_a: float, start_b: float, end_b: float) -> float:
    return max(0.0, min(end_a, end_b) - max(start_a, start_b))


def _select_segment_for_line(line: Line, segments: Sequence[Segment]) -> Segment:
    """Choose the segment where ``line`` has the greatest overlap.

    If there is a tie, the line is assigned to the segment that contains the
    line midpoint; if the midpoint also lies on a boundary, the earliest segment
    is chosen for determinism.
    """

    overlaps = [
        _compute_overlap(line.start, line.end, segment.start, segment.end)
        for segment in segments
    ]
    max_overlap = max(overlaps)
    # Midpoint helps break ties at boundaries.
    midpoint = (line.start + line.end) / 2
    midpoint_segment = next(
        (
            segment
            for segment in segments
            if segment.start <= midpoint < segment.end
        ),
        segments[0],
    )

    # Prefer the segment with the largest overlap; on ties, use midpoint.
    candidate_indices = [i for i, overlap in enumerate(overlaps) if overlap == max_overlap]
    if len(candidate_indices) == 1:
        return segments[candidate_indices[0]]
    if midpoint_segment.index in candidate_indices:
        return midpoint_segment
    return segments[candidate_indices[0]]


def build_segments(
    lines: Iterable[dict | Line],
    segment_length: float = 30.0,
    total_duration: float | None = None,
) -> List[Segment]:
    """Return a list of fixed-length segments with lines assigned by majority coverage.

    Parameters
    ----------
    lines:
        Iterable of dicts or :class:`Line` objects with ``start``, ``end``, and
        ``text`` fields. Lines are kept intact; if they straddle a boundary, they
        are assigned to the segment where they spend the most time.
    segment_length:
        Length of each segment in seconds (defaults to 30.0 seconds).
    total_duration:
        Optional overall duration. When omitted, the end of the last line is
        used to calculate how many segments are needed.

    Returns
    -------
    List[Segment]
        Segments covering the entire duration. The ``text`` property on each
        segment concatenates its lines, preserving their order.
    """

    normalized_lines = [line if isinstance(line, Line) else Line(**line) for line in lines]
    if not normalized_lines:
        return []

    last_end = max(line.end for line in normalized_lines)
    duration = total_duration if total_duration is not None else last_end
    segment_count = max(1, ceil(duration / segment_length))

    segments = [
        Segment(index=i, start=i * segment_length, end=(i + 1) * segment_length)
        for i in range(segment_count)
    ]

    for line in normalized_lines:
        target_segment = _select_segment_for_line(line, segments)
        target_segment.lines.append(line)

    # Sort lines within each segment for stable, chronological output.
    for segment in segments:
        segment.lines.sort(key=lambda ln: ln.start)

    return segments


__all__ = [
    "Line",
    "Segment",
    "build_segments",
]
