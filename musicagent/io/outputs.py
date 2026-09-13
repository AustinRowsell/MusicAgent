"""Local filesystem output store."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

from musicagent.models import GeneratedAsset, ProjectPaths, ProjectRequest


class LocalOutputStore:
    """Create project output folders and manifests."""

    def create_project(self, request: ProjectRequest) -> ProjectPaths:
        project_root = request.output_root / slugify(request.name)
        if project_root.exists() and not request.overwrite:
            raise FileExistsError(f"Project output already exists: {project_root}")

        midi_dir = project_root / "midi"
        data_dir = project_root / "data"
        inputs_dir = project_root / "inputs"
        midi_dir.mkdir(parents=True, exist_ok=request.overwrite)
        data_dir.mkdir(parents=True, exist_ok=True)
        inputs_dir.mkdir(parents=True, exist_ok=True)
        return ProjectPaths(
            root=project_root, midi_dir=midi_dir, data_dir=data_dir, inputs_dir=inputs_dir
        )

    def write_text(self, project: ProjectPaths, relative_path: str, content: str) -> Path:
        target = project.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return target

    def write_json(self, project: ProjectPaths, relative_path: str, data: object) -> Path:
        target = project.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2, sort_keys=True))
        return target

    def write_manifest(
        self,
        project: ProjectPaths,
        request: ProjectRequest,
        assets: list[GeneratedAsset],
    ) -> Path:
        manifest = {
            "project": request.name,
            "crew": request.crew,
            "prompt": request.prompt,
            "tempo_bpm": request.tempo_bpm,
            "key": request.key,
            "time_signature": request.time_signature,
            "created_at": datetime.now(UTC).isoformat(),
            "assets": [asset.relative_to(project.root) for asset in assets],
        }
        return self.write_json(project, "session_manifest.json", manifest)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError("Project name must contain at least one alphanumeric character")
    return slug
