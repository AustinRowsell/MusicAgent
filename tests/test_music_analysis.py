from pathlib import Path

from musicagent.midi.analysis import PrettyMidiAnalyzer
from musicagent.midi.events import MidiNote, MidiTrack
from musicagent.midi.writer import MidoMidiWriter
from musicagent.theory.harmony import Music21HarmonyValidator


def test_pretty_midi_analyzer_reports_instrument_notes(tmp_path: Path):
    track = MidiTrack(
        name="lead", notes=(MidiNote(pitch=72, start_beats=0, duration_beats=1, velocity=90),)
    )
    midi_path = MidoMidiWriter().write_track(track, tmp_path, tempo_bpm=100)

    summary = PrettyMidiAnalyzer().summarise(midi_path)

    assert summary.instrument_count == 1
    assert summary.note_count == 1
    assert summary.pitch_range == (72, 72)


def test_music21_validator_accepts_c_major_triad():
    result = Music21HarmonyValidator().validate_chord([60, 64, 67], key_name="C")

    assert result.is_valid
    assert result.chord_name
    assert result.key_name == "C"
