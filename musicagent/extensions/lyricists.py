"""Lyricist persona creation workflow."""

from __future__ import annotations

import json
from pathlib import Path

from musicagent.models import AgentDefinition


class LyricistPersonaCreator:
    """Create file-backed lyricist personas without changing core registries."""

    def __init__(self, persona_dir: Path) -> None:
        self._persona_dir = persona_dir

    def create(
        self,
        persona_id: str,
        display_name: str,
        role: str,
        responsibilities: tuple[str, ...],
    ) -> AgentDefinition:
        persona = AgentDefinition(
            id=persona_id,
            display_name=display_name,
            role=role,
            responsibilities=responsibilities,
        )
        self._persona_dir.mkdir(parents=True, exist_ok=True)
        target = self._persona_dir / f"{persona_id}.json"
        target.write_text(json.dumps(persona.model_dump(), indent=2, sort_keys=True))
        return persona
