"""Core domain models for MusicAgent."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InputMaterialType(str, Enum):
    """Supported first-version input material types."""

    TEXT_PROMPT = "text_prompt"
    TEXT = "text"
    MARKDOWN = "markdown"
    MIDI = "midi"
    JSON = "json"


class InputMaterial(BaseModel):
    """Normalised representation of user-provided material."""

    model_config = ConfigDict(frozen=True)

    id: str
    type: InputMaterialType
    path: Path | None = None
    content: str | None = None
    description: str = ""
    assigned_agents: tuple[str, ...] = ()
    priority: str = "medium"
    constraints: tuple[str, ...] = ()


class ProjectRequest(BaseModel):
    """User request for a project generation run."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    name: str
    prompt: str
    output_root: Path = Path("outputs")
    crew: str = "electronic_alt_pop"
    tempo_bpm: int = Field(default=120, ge=20, le=300)
    key: str = "C major"
    time_signature: str = "4/4"
    inputs: tuple[InputMaterial, ...] = ()
    overwrite: bool = False
    dry_run: bool = False
    review_pass: bool = False

    @field_validator("output_root", mode="before")
    @classmethod
    def expand_output_root(cls, value: str | Path) -> Path:
        return Path(value).expanduser()


class ProjectPaths(BaseModel):
    """Created output paths for a project run."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    root: Path
    midi_dir: Path
    data_dir: Path
    inputs_dir: Path


class GeneratedAsset(BaseModel):
    """A generated file written by the system."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    kind: str
    path: Path
    description: str = ""

    def relative_to(self, root: Path) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "path": str(self.path.relative_to(root)),
            "description": self.description,
        }


class AgentDefinition(BaseModel):
    """Registry definition for a crew member."""

    model_config = ConfigDict(frozen=True)

    id: str
    display_name: str
    role: str
    responsibilities: tuple[str, ...]


class CrewDefinition(BaseModel):
    """Registry definition for a built-in or user-provided crew."""

    model_config = ConfigDict(frozen=True)

    id: str
    display_name: str
    style_aliases: tuple[str, ...]
    required_agents: tuple[str, ...]
    optional_agents: tuple[str, ...] = ()
    accepted_input_types: tuple[InputMaterialType, ...]
    produced_output_types: tuple[str, ...]
    default_style_pack: str
    compatible_style_packs: tuple[str, ...]
    default_task_graph: tuple[str, ...]


class StylePack(BaseModel):
    """Configurable musical assumptions for a style or genre."""

    model_config = ConfigDict(frozen=True)

    id: str
    display_name: str
    tempo_range: tuple[int, int]
    common_keys: tuple[str, ...]
    instrumentation: tuple[str, ...]
    recommended_agents: tuple[str, ...]


class MidiAnalysisSummary(BaseModel):
    """High-level summary of a MIDI file."""

    model_config = ConfigDict(frozen=True)

    instrument_count: int
    note_count: int
    pitch_range: tuple[int, int] | None


class HarmonyValidationResult(BaseModel):
    """Result of theory-aware harmony validation."""

    model_config = ConfigDict(frozen=True)

    is_valid: bool
    chord_name: str
    key_name: str
    message: str = ""
