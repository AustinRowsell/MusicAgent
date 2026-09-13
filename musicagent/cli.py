"""Command-line interface for MusicAgent."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from musicagent.io.inputs import InputMaterialReader
from musicagent.models import InputHandlingMode, ProjectRequest
from musicagent.orchestration.crew import CrewProjectGenerator
from musicagent.registries.agents import built_in_agents
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


@app.command("crew-worker")
def crew_worker(crew_id: Annotated[str, typer.Option("--crew-id")]) -> None:
    """Start a lightweight placeholder worker for a configured crew."""

    crew = BuiltInCrewRegistry.default().resolve(crew_id)
    console.print(f"crew worker ready: {crew.id}")


@app.command("agent-worker")
def agent_worker(agent_id: Annotated[str, typer.Option("--agent-id")]) -> None:
    """Start a lightweight placeholder worker for a configured agent."""

    agent_ids = {agent.id for agent in built_in_agents()}
    if agent_id not in agent_ids:
        raise typer.BadParameter(f"Unknown agent: {agent_id}")
    console.print(f"agent worker ready: {agent_id}")


@app.command("create")
def create_project(
    name: Annotated[str, typer.Option("--name")],
    prompt: Annotated[str, typer.Option("--prompt")],
    output: Annotated[Path, typer.Option("--output")],
    crew: Annotated[str, typer.Option("--crew")] = "electronic_alt_pop",
    input_paths: Annotated[list[Path] | None, typer.Option("--input")] = None,
    input_mode: Annotated[InputHandlingMode, typer.Option("--input-mode")] = InputHandlingMode.COPY,
    tempo: Annotated[int, typer.Option("--tempo")] = 120,
    key: Annotated[str, typer.Option("--key")] = "C major",
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
    overwrite: Annotated[bool, typer.Option("--overwrite")] = False,
) -> None:
    """Create a project output folder and deterministic crew outputs."""

    input_reader = InputMaterialReader()
    materials = tuple(input_reader.from_path(path) for path in input_paths or [])
    request = ProjectRequest(
        name=name,
        prompt=prompt,
        output_root=output,
        crew=crew,
        tempo_bpm=tempo,
        key=key,
        inputs=materials,
        input_mode=input_mode,
        dry_run=dry_run,
        overwrite=overwrite,
    )
    result = CrewProjectGenerator(input_reader=input_reader).generate(request)
    console.print(
        f"Created {request.name} with {len(result.assets)} assets using {result.crew.id}."
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
