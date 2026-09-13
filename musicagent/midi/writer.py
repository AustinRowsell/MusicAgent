"""Mido-backed MIDI writer."""

from __future__ import annotations

from pathlib import Path

import mido

from musicagent.midi.events import MidiNote, MidiTrack


class MidoMidiWriter:
    """Write standalone MIDI files per track/instrument."""

    ticks_per_beat = 480

    def write_tracks(
        self,
        tracks: list[MidiTrack],
        output_dir: Path,
        tempo_bpm: int,
    ) -> dict[str, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        return {track.name: self.write_track(track, output_dir, tempo_bpm) for track in tracks}

    def write_track(self, track: MidiTrack, output_dir: Path, tempo_bpm: int) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        midi_file = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        midi_track = mido.MidiTrack()
        midi_file.tracks.append(midi_track)
        midi_track.append(mido.MetaMessage("track_name", name=track.name, time=0))
        midi_track.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo_bpm), time=0))
        if track.program and track.program > 0:
            midi_track.append(mido.Message("program_change", program=track.program, time=0))
        self._append_notes(midi_track, track.notes)
        target = output_dir / track.safe_filename
        midi_file.save(target)
        return target

    def write_preview(self, tracks: list[MidiTrack], output_dir: Path, tempo_bpm: int) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        midi_file = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        for track in tracks:
            midi_track = mido.MidiTrack()
            midi_file.tracks.append(midi_track)
            midi_track.append(mido.MetaMessage("track_name", name=track.name, time=0))
            midi_track.append(
                mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(tempo_bpm), time=0)
            )
            self._append_notes(midi_track, track.notes)
        target = output_dir / "preview_full_sketch.mid"
        midi_file.save(target)
        return target

    def _append_notes(self, midi_track: mido.MidiTrack, notes: tuple[MidiNote, ...]) -> None:
        timed_events: list[tuple[int, int, MidiNote]] = []
        for note in notes:
            start_tick = round(note.start_beats * self.ticks_per_beat)
            end_tick = round((note.start_beats + note.duration_beats) * self.ticks_per_beat)
            timed_events.append((start_tick, 0, note))
            timed_events.append((end_tick, 1, note))

        previous_tick = 0
        for absolute_tick, event_order, note in sorted(
            timed_events, key=lambda event: (event[0], event[1])
        ):
            delta = absolute_tick - previous_tick
            previous_tick = absolute_tick
            if event_order == 0:
                midi_track.append(
                    mido.Message(
                        "note_on",
                        note=note.pitch,
                        velocity=note.velocity,
                        channel=note.channel,
                        time=delta,
                    )
                )
            else:
                midi_track.append(
                    mido.Message(
                        "note_off",
                        note=note.pitch,
                        velocity=0,
                        channel=note.channel,
                        time=delta,
                    )
                )
