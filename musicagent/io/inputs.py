"""Input material readers."""

from __future__ import annotations

from pathlib import Path

from musicagent.models import InputMaterial, InputMaterialType


class InputMaterialReader:
    """Create normalised input materials from user input."""

    def from_prompt(self, prompt: str) -> InputMaterial:
        return InputMaterial(
            id="main_prompt",
            type=InputMaterialType.TEXT_PROMPT,
            content=prompt,
            assigned_agents=("brief",),
            priority="high",
        )

    def from_path(self, path: Path) -> InputMaterial:
        resolved_path = path.expanduser()
        material_type = self._detect_type(resolved_path)
        binary_or_metadata_only = material_type in {InputMaterialType.MIDI, InputMaterialType.AUDIO}
        content = None if binary_or_metadata_only else resolved_path.read_text()
        constraints = ("metadata_only",) if material_type is InputMaterialType.AUDIO else ()
        return InputMaterial(
            id=resolved_path.stem,
            type=material_type,
            path=resolved_path,
            content=content,
            constraints=constraints,
            metadata={"extension": resolved_path.suffix.lower()},
        )

    @staticmethod
    def _detect_type(path: Path) -> InputMaterialType:
        suffix = path.suffix.lower()
        if suffix in {".md", ".markdown"}:
            return InputMaterialType.MARKDOWN
        if suffix in {".mid", ".midi"}:
            return InputMaterialType.MIDI
        if suffix in {".wav", ".mp3", ".aiff", ".aif", ".flac", ".ogg"}:
            return InputMaterialType.AUDIO
        if suffix == ".json":
            return InputMaterialType.JSON
        return InputMaterialType.TEXT
