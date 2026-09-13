"""Crew project generation workflow."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from musicagent.io.inputs import InputMaterialReader
from musicagent.io.outputs import LocalOutputStore
from musicagent.midi.writer import MidoMidiWriter
from musicagent.models import (
    CrewDefinition,
    GeneratedAsset,
    InputHandlingMode,
    ProjectPaths,
    ProjectRequest,
)
from musicagent.orchestration.llm import StubLLMClient
from musicagent.orchestration.tasks import build_stub_task_result, tasks_for_crew, tracks_for_crew
from musicagent.registries.crews import BuiltInCrewRegistry


class AgentRunner(Protocol):
    """Small interface for executing an agent task."""

    def run(self, agent_id: str, prompt: str) -> str:
        """Return an agent response for a task prompt."""


@dataclass(frozen=True)
class StubAgentRunner:
    """Deterministic runner for tests and local development."""

    llm_client: StubLLMClient = field(default_factory=StubLLMClient)

    def run(self, agent_id: str, prompt: str) -> str:
        return self.llm_client.complete(agent_id, prompt)


@dataclass(frozen=True)
class CrewGenerationResult:
    """Result of a crew generation workflow."""

    crew: CrewDefinition
    project: ProjectPaths
    assets: tuple[GeneratedAsset, ...]
    executed_agents: tuple[str, ...]


class CrewProjectGenerator:
    """Generate deterministic Phase 3-4 project outputs through crew task graphs."""

    def __init__(
        self,
        agent_runner: AgentRunner | None = None,
        crew_registry: BuiltInCrewRegistry | None = None,
        output_store: LocalOutputStore | None = None,
        midi_writer: MidoMidiWriter | None = None,
        input_reader: InputMaterialReader | None = None,
    ) -> None:
        self._agent_runner = agent_runner or StubAgentRunner()
        self._crew_registry = crew_registry or BuiltInCrewRegistry.default()
        self._output_store = output_store or LocalOutputStore()
        self._midi_writer = midi_writer or MidoMidiWriter()
        self._input_reader = input_reader or InputMaterialReader()

    def generate(self, request: ProjectRequest) -> CrewGenerationResult:
        crew = self._crew_registry.resolve(request.crew)
        canonical_request = request.model_copy(update={"crew": crew.id})
        project = self._output_store.create_project(canonical_request)
        assets: list[GeneratedAsset] = []

        assets.extend(self._copy_inputs(project, canonical_request))
        brief_path = self._write_brief(project, canonical_request, crew)
        assets.append(GeneratedAsset(kind="markdown", path=brief_path, description="Project brief"))

        executed_agents: list[str] = []
        for task in tasks_for_crew(crew.id):
            response = self._agent_runner.run(task.agent_id, canonical_request.prompt)
            task_result = build_stub_task_result(task, canonical_request, response)
            markdown_path = self._output_store.write_text(
                project, task_result.markdown_path, task_result.markdown
            )
            data_path = self._output_store.write_json(
                project, task_result.data_path, task_result.data
            )
            assets.append(
                GeneratedAsset(kind="markdown", path=markdown_path, description=task.title)
            )
            assets.append(GeneratedAsset(kind="json", path=data_path, description=task.title))
            executed_agents.append(task.agent_id)

        if canonical_request.review_pass:
            review_response = self._agent_runner.run("reviewer", canonical_request.prompt)
            review_markdown = chr(10).join(
                ["# Review", "", "Agent: reviewer", "", review_response, ""]
            )
            review_path = self._output_store.write_text(project, "review.md", review_markdown)
            review_data_path = self._output_store.write_json(
                project,
                "data/review.json",
                {"agent_id": "reviewer", "summary": review_response},
            )
            assets.append(GeneratedAsset(kind="markdown", path=review_path, description="Review"))
            assets.append(GeneratedAsset(kind="json", path=review_data_path, description="Review"))
            executed_agents.append("reviewer")

        for track_name, midi_path in self._midi_writer.write_tracks(
            tracks_for_crew(crew.id), project.midi_dir, canonical_request.tempo_bpm
        ).items():
            assets.append(
                GeneratedAsset(kind="midi", path=midi_path, description=f"{track_name} MIDI")
            )

        manifest_path = self._output_store.write_manifest(project, canonical_request, assets)
        assets.append(
            GeneratedAsset(kind="manifest", path=manifest_path, description="Session manifest")
        )
        return CrewGenerationResult(
            crew=crew,
            project=project,
            assets=tuple(assets),
            executed_agents=tuple(executed_agents),
        )

    def _copy_inputs(self, project: ProjectPaths, request: ProjectRequest) -> list[GeneratedAsset]:
        assets: list[GeneratedAsset] = []
        for material in request.inputs:
            if material.path is None:
                continue
            if request.input_mode is InputHandlingMode.REFERENCE:
                assets.append(
                    GeneratedAsset(
                        kind="input_reference", path=material.path, description=material.id
                    )
                )
                continue
            target = project.inputs_dir / material.path.name
            shutil.copyfile(material.path, target)
            assets.append(GeneratedAsset(kind="input", path=target, description=material.id))
        return assets

    def _write_brief(
        self, project: ProjectPaths, request: ProjectRequest, crew: CrewDefinition
    ) -> Path:
        content = chr(10).join(
            [
                f"# {request.name}",
                "",
                f"Prompt: {request.prompt}",
                f"Crew: {crew.id}",
                f"Tempo: {request.tempo_bpm}",
                f"Key: {request.key}",
                "",
            ]
        )
        return self._output_store.write_text(project, "brief.md", content)
