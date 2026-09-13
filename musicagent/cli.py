"""Command-line interface for MusicAgent."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from musicagent.io.outputs import LocalOutputStore
from musicagent.midi.events import MidiNote, MidiTrack
from musicagent.midi.writer import MidoMidiWriter
from musicagent.models import GeneratedAsset, ProjectRequest
from musicagent.registries.crews import BuiltInCrewRegistry

app = typer.Typer(help="Multi-agent music creation tool.")
console = Console()


@app.command("crews")
def list_crews() -> None:
    """List built-in crews."""

    registry = BuiltInCrewRegistry.default()
    for crew in registry.list():
        aliases = ", ".join(crew.style_aliases)
        console.print(f"{crew.id}: {crew.display_name} [{aliases}]")


@app.command("create")
def create_project(
    name: Annotated[str, typer.Option("--name")],
    prompt: Annotated[str, typer.Option("--prompt")],
    output: Annotated[Path, typer.Option("--output")],
    crew: Annotated[str, typer.Option("--crew")] = "electronic_alt_pop",
    tempo: Annotated[int, typer.Option("--tempo")] = 120,
    key: Annotated[str, typer.Option("--key")] = "C major",
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    overwrite: Annotated[bool, typer.Option("--overwrite")] = False,
) -> None:
    """Create a project output folder and deterministic dry-run assets."""

    registry = BuiltInCrewRegistry.default()
    crew_definition = registry.resolve(crew)
    request = ProjectRequest(
        name=name,
        prompt=prompt,
        output_root=output,
        crew=crew_definition.id,
        tempo_bpm=tempo,
        key=key,
        dry_run=dry_run,
        overwrite=overwrite,
    )
    if not dry_run:
        raise typer.BadParameter(
            "Phase 1-2 supports --dry-run only; agent orchestration starts in Phase 3."
        )

    assets = DryRunProjectGenerator().generate(request)
    console.print(f"Created {request.name} with {len(assets)} assets using {crew_definition.id}.")


def main() -> None:
    app()


class DryRunProjectGenerator:
    """Deterministic output generator for tests and offline development."""

    def __init__(self) -> None:
        self._store = LocalOutputStore()
        self._midi_writer = MidoMidiWriter()

    def generate(self, request: ProjectRequest) -> list[GeneratedAsset]:
        project = self._store.create_project(request)
        assets: list[GeneratedAsset] = []

        brief_content = chr(10).join(
            [
                f"# {request.name}",
                "",
                f"Prompt: {request.prompt}",
                f"Crew: {request.crew}",
                "",
            ]
        )
        brief_path = self._store.write_text(project, "brief.md", brief_content)
        assets.append(GeneratedAsset(kind="markdown", path=brief_path, description="Project brief"))

        tracks = self._tracks_for_crew(request.crew)
        for track_name, path in self._midi_writer.write_tracks(
            tracks, project.midi_dir, request.tempo_bpm
        ).items():
            assets.append(GeneratedAsset(kind="midi", path=path, description=f"{track_name} MIDI"))

        manifest_path = self._store.write_manifest(project, request, assets)
        assets.append(
            GeneratedAsset(kind="manifest", path=manifest_path, description="Session manifest")
        )
        return assets

    @staticmethod
    def _tracks_for_crew(crew: str) -> list[MidiTrack]:
        if crew == "singer_songwriter_acoustic":
            return [
                MidiTrack(
                    name="vocal_melody",
                    notes=(
                        MidiNote(pitch=64, start_beats=0, duration_beats=1, velocity=86),
                        MidiNote(pitch=67, start_beats=1, duration_beats=1, velocity=88),
                    ),
                ),
                MidiTrack(
                    name="accompaniment",
                    notes=(
                        MidiNote(pitch=48, start_beats=0, duration_beats=2, velocity=72),
                        MidiNote(pitch=55, start_beats=0, duration_beats=2, velocity=68),
                        MidiNote(pitch=60, start_beats=0, duration_beats=2, velocity=66),
                    ),
                ),
            ]
        return [
            MidiTrack(
                name="drums",
                notes=(
                    MidiNote(pitch=36, start_beats=0, duration_beats=0.25, velocity=110, channel=9),
                    MidiNote(pitch=38, start_beats=1, duration_beats=0.25, velocity=95, channel=9),
                    MidiNote(
                        pitch=42, start_beats=0.5, duration_beats=0.25, velocity=70, channel=9
                    ),
                ),
            ),
            MidiTrack(
                name="bass",
                notes=(MidiNote(pitch=45, start_beats=0, duration_beats=1, velocity=92),),
            ),
            MidiTrack(
                name="chords",
                notes=(
                    MidiNote(pitch=57, start_beats=0, duration_beats=2, velocity=76),
                    MidiNote(pitch=60, start_beats=0, duration_beats=2, velocity=72),
                    MidiNote(pitch=64, start_beats=0, duration_beats=2, velocity=70),
                ),
            ),
            MidiTrack(
                name="hooks",
                notes=(MidiNote(pitch=72, start_beats=1, duration_beats=0.5, velocity=86),),
            ),
        ]


if __name__ == "__main__":
    main()
