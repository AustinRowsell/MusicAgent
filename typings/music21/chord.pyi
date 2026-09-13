from collections.abc import Sequence

from music21.pitch import Pitch

class Chord:
    pitches: list[Pitch]
    pitchedCommonName: str
    def __init__(self, notes: Sequence[object]) -> None: ...
