import mido
from musicagent.midi.events import MidiNote, MidiTrack
from musicagent.midi.writer import MidoMidiWriter
from musicagent.registries.styles import BuiltInStyleRegistry


def test_midi_writer_adds_general_midi_program_changes(tmp_path):
    track = MidiTrack(
        name="bass",
        notes=(MidiNote(pitch=45, start_beats=0, duration_beats=1, velocity=90),),
        program=33,
    )

    path = MidoMidiWriter().write_track(track, tmp_path, tempo_bpm=120)
    midi = mido.MidiFile(path)

    assert any(
        message.type == "program_change" and message.program == 33 for message in midi.tracks[0]
    )


def test_drum_track_uses_zero_based_channel_nine(tmp_path):
    track = MidiTrack(
        name="drums",
        notes=(MidiNote(pitch=36, start_beats=0, duration_beats=0.25, velocity=100, channel=9),),
    )

    path = MidoMidiWriter().write_track(track, tmp_path, tempo_bpm=120)
    midi = mido.MidiFile(path)

    note_on = next(message for message in midi.tracks[0] if message.type == "note_on")
    assert note_on.channel == 9


def test_electronic_radio_pop_and_club_styles_have_distinct_structures():
    registry = BuiltInStyleRegistry.default()

    radio = registry.get("electronic_radio_pop")
    club = registry.get("electronic_club_extended")

    assert radio.structure != club.structure
    assert radio.structure_profile == "radio_pop"
    assert club.structure_profile == "club_extended"


def test_acoustic_default_style_is_guitar_first():
    style = BuiltInStyleRegistry.default().get("singer_songwriter_acoustic")

    assert style.accompaniment_default == "guitar_first"
