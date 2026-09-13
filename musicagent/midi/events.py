"""MIDI event domain models."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class MidiNote:
    """A beat-based MIDI note event."""

    pitch: int
    start_beats: float
    duration_beats: float
    velocity: int
    channel: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.pitch <= 127:
            raise ValueError("MIDI pitch must be between 0 and 127")
        if self.start_beats < 0:
            raise ValueError("MIDI note start must not be negative")
        if self.duration_beats <= 0:
            raise ValueError("MIDI note duration must be positive")
        if not 0 <= self.velocity <= 127:
            raise ValueError("MIDI velocity must be between 0 and 127")
        if not 0 <= self.channel <= 15:
            raise ValueError("MIDI channel must be between 0 and 15")


@dataclass(frozen=True)
class MidiTrack:
    """A standalone MIDI track/instrument export."""

    name: str
    notes: tuple[MidiNote, ...]
    program: int = 0

    @property
    def safe_filename(self) -> str:
        filename = re.sub(r"[^a-zA-Z0-9]+", "_", self.name.strip().lower()).strip("_")
        if not filename:
            raise ValueError("MIDI track name must contain at least one alphanumeric character")
        return f"{filename}.mid"
