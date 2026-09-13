"""music21-backed harmony validation."""

from __future__ import annotations

from music21 import chord, key, pitch

from musicagent.models import HarmonyValidationResult


class Music21HarmonyValidator:
    """Validate simple harmonic material with music21."""

    def validate_chord(self, midi_pitches: list[int], key_name: str) -> HarmonyValidationResult:
        if not midi_pitches:
            return HarmonyValidationResult(
                is_valid=False,
                chord_name="",
                key_name=key_name,
                message="Chord must contain at least one pitch.",
            )

        analysed_key = key.Key(key_name)
        analysed_chord = chord.Chord([pitch.Pitch(midi=value) for value in midi_pitches])
        chord_name = analysed_chord.pitchedCommonName
        invalid_pitches = [
            note.name
            for note in analysed_chord.pitches
            if analysed_key.getScale().getScaleDegreeFromPitch(note) is None
        ]
        if invalid_pitches:
            return HarmonyValidationResult(
                is_valid=False,
                chord_name=chord_name,
                key_name=key_name,
                message=f"Pitches outside key: {', '.join(invalid_pitches)}",
            )
        return HarmonyValidationResult(is_valid=True, chord_name=chord_name, key_name=key_name)
