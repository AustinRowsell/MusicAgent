"""pretty_midi-backed MIDI analysis."""

from __future__ import annotations

from pathlib import Path

import pretty_midi

from musicagent.models import MidiAnalysisSummary


class PrettyMidiAnalyzer:
    """Summarise MIDI files at a musical-note level."""

    def summarise(self, path: Path) -> MidiAnalysisSummary:
        midi = pretty_midi.PrettyMIDI(str(path))
        instruments = [instrument for instrument in midi.instruments if instrument.notes]
        pitches = [note.pitch for instrument in instruments for note in instrument.notes]
        pitch_range = (min(pitches), max(pitches)) if pitches else None
        return MidiAnalysisSummary(
            instrument_count=len(instruments),
            note_count=len(pitches),
            pitch_range=pitch_range,
        )
