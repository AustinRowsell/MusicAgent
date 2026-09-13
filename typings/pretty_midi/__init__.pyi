class Note:
    pitch: int

class Instrument:
    notes: list[Note]

class PrettyMIDI:
    instruments: list[Instrument]
    def __init__(self, midi_file: str | None = None) -> None: ...
