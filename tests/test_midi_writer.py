from pathlib import Path

import mido
from musicagent.midi.events import MidiNote, MidiTrack
from musicagent.midi.writer import MidoMidiWriter


def test_writer_creates_one_file_per_track(tmp_path: Path):
    tracks = [
        MidiTrack(
            name="bass", notes=(MidiNote(pitch=45, start_beats=0, duration_beats=1, velocity=90),)
        ),
        MidiTrack(
            name="lead", notes=(MidiNote(pitch=72, start_beats=1, duration_beats=1, velocity=85),)
        ),
    ]

    written = MidoMidiWriter().write_tracks(tracks, tmp_path, tempo_bpm=120)

    assert set(written) == {"bass", "lead"}
    assert (tmp_path / "bass.mid").exists()
    assert (tmp_path / "lead.mid").exists()
    assert not (tmp_path / "full_sketch.mid").exists()


def test_written_midi_file_is_valid(tmp_path: Path):
    tracks = [
        MidiTrack(
            name="chords", notes=(MidiNote(pitch=60, start_beats=0, duration_beats=2, velocity=80),)
        )
    ]

    MidoMidiWriter().write_tracks(tracks, tmp_path, tempo_bpm=90)

    midi_file = mido.MidiFile(tmp_path / "chords.mid")
    assert len(midi_file.tracks) == 1
    assert any(message.type == "note_on" for message in midi_file.tracks[0])


def test_preview_file_is_optional_and_named_explicitly(tmp_path: Path):
    tracks = [
        MidiTrack(
            name="drums",
            notes=(
                MidiNote(pitch=36, start_beats=0, duration_beats=0.25, velocity=100, channel=9),
            ),
        ),
        MidiTrack(
            name="bass", notes=(MidiNote(pitch=45, start_beats=0, duration_beats=1, velocity=90),)
        ),
    ]

    preview = MidoMidiWriter().write_preview(tracks, tmp_path, tempo_bpm=120)

    assert preview.name == "preview_full_sketch.mid"
    assert preview.exists()
    assert not (tmp_path / "full_sketch.mid").exists()
