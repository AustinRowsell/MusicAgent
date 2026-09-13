"""Lyricist persona registry."""

from __future__ import annotations

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
