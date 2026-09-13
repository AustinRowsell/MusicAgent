"""Regeneration workflow for individual MIDI parts."""

from __future__ import annotations

from musicagent.midi.events import MidiNote, MidiTrack
from musicagent.midi.writer import MidoMidiWriter
from musicagent.models import ProjectPaths


class RegenerationService:
    """Regenerate one named MIDI part without touching unrelated tracks."""

    def __init__(self, midi_writer: MidoMidiWriter | None = None) -> None:
        self._midi_writer = midi_writer or MidoMidiWriter()

    def regenerate_part(self, project: ProjectPaths, part_name: str, tempo_bpm: int) -> None:
        track = MidiTrack(
            name=part_name,
            notes=(
                MidiNote(pitch=47, start_beats=0, duration_beats=0.5, velocity=101),
                MidiNote(pitch=50, start_beats=0.5, duration_beats=0.5, velocity=96),
            ),
        )
        self._midi_writer.write_track(track, project.midi_dir, tempo_bpm)
