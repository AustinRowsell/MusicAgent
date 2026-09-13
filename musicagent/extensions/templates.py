"""Project templates and batch manifest workflows."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from musicagent.models import ProjectRequest
from musicagent.orchestration.crew import CrewGenerationResult, CrewProjectGenerator


class ProjectTemplate(BaseModel):
    """Reusable project defaults for rapid creation."""

    model_config = ConfigDict(frozen=True)

    id: str
    crew: str
    tempo_bpm: int = Field(ge=20, le=300)
    key: str


class ProjectTemplateStore:
    """File-backed project template store."""

    def __init__(self, template_dir: Path) -> None:
        self._template_dir = template_dir

    def create_template(
        self, template_id: str, crew: str, tempo_bpm: int, key: str
    ) -> ProjectTemplate:
        template = ProjectTemplate(id=template_id, crew=crew, tempo_bpm=tempo_bpm, key=key)
        self._template_dir.mkdir(parents=True, exist_ok=True)
        (self._template_dir / f"{template_id}.json").write_text(
            json.dumps(template.model_dump(), indent=2, sort_keys=True)
        )
        return template

    def get(self, template_id: str) -> ProjectTemplate:
        data = json.loads((self._template_dir / f"{template_id}.json").read_text())
        return ProjectTemplate.model_validate(data)


class BatchProjectRunner:
    """Run multiple projects from a manifest."""

    def __init__(
        self,
        template_store: ProjectTemplateStore,
        generator: CrewProjectGenerator | None = None,
    ) -> None:
        self._template_store = template_store
        self._generator = generator or CrewProjectGenerator()

    def run_manifest(self, manifest_path: Path, output_root: Path) -> list[CrewGenerationResult]:
        manifest = json.loads(manifest_path.read_text())
        results: list[CrewGenerationResult] = []
        for project_data in manifest["projects"]:
            template = (
                self._template_store.get(project_data["template"])
                if "template" in project_data
                else None
            )
            crew = project_data.get("crew", template.crew if template else "electronic_alt_pop")
            tempo_bpm = project_data.get("tempo_bpm", template.tempo_bpm if template else 120)
            key = project_data.get("key", template.key if template else "C major")
            request = ProjectRequest(
                name=project_data["name"],
                prompt=project_data["prompt"],
                output_root=output_root,
                crew=crew,
                tempo_bpm=tempo_bpm,
                key=key,
                dry_run=True,
            )
            results.append(self._generator.generate(request))
        return results
