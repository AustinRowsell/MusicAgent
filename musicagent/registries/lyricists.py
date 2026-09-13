"""Lyricist persona registries."""

from __future__ import annotations

import json
from pathlib import Path

from musicagent.models import AgentDefinition


class BuiltInLyricistRegistry:
    """Registry for built-in lyricist personas."""

    @classmethod
    def default(cls) -> BuiltInLyricistRegistry:
        return cls()

    def get(self, lyricist_id: str) -> AgentDefinition:
        if lyricist_id != "lyricist_poet":
            raise KeyError(f"Unknown lyricist persona: {lyricist_id}")
        return AgentDefinition(
            id="lyricist_poet",
            display_name="Lyricist / Poet",
            role="Lyrics, metaphor, narrative, and rhyme specialist",
            responsibilities=("theme", "metaphor", "emotional weight", "complex rhyme"),
        )


class FileLyricistRegistry:
    """Registry for user-created lyricist personas stored as JSON files."""

    def __init__(self, persona_dir: Path) -> None:
        self._persona_dir = persona_dir

    def get(self, lyricist_id: str) -> AgentDefinition:
        path = self._persona_dir / f"{lyricist_id}.json"
        if not path.exists():
            raise KeyError(f"Unknown lyricist persona: {lyricist_id}")
        return AgentDefinition.model_validate(json.loads(path.read_text()))
