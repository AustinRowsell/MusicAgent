"""Runtime configuration contracts for answered product decisions."""

from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, ConfigDict

InputModeSetting = Literal["copy", "reference"]
DeploymentProfileSetting = Literal["app", "crew", "agent"]


class MusicAgentSettings(BaseModel):
    """Typed configuration for decision-gated runtime behaviour."""

    model_config = ConfigDict(frozen=True)

    interface_mode: Literal["both"] = "both"
    midi_metadata_mode: Literal["names_and_general_midi"] = "names_and_general_midi"
    input_mode: InputModeSetting = "copy"
    audio_mode: Literal["metadata_only"] = "metadata_only"
    llm_provider: str = "stub"
    model_provider_mode: Literal["fully_pluggable"] = "fully_pluggable"
    output_path_mode: Literal["relative_and_absolute"] = "relative_and_absolute"
    electronic_structure_mode: Literal["style_pack"] = "style_pack"
    acoustic_accompaniment_default: Literal["guitar_first"] = "guitar_first"
    deployment_profile: DeploymentProfileSetting = "app"
    has_openai_api_key: bool = False

    def public_snapshot(self) -> dict[str, str | bool]:
        """Return non-secret settings for diagnostics/manifests."""

        return {
            "interface_mode": self.interface_mode,
            "midi_metadata_mode": self.midi_metadata_mode,
            "input_mode": self.input_mode,
            "audio_mode": self.audio_mode,
            "llm_provider": self.llm_provider,
            "model_provider_mode": self.model_provider_mode,
            "output_path_mode": self.output_path_mode,
            "electronic_structure_mode": self.electronic_structure_mode,
            "acoustic_accompaniment_default": self.acoustic_accompaniment_default,
            "deployment_profile": self.deployment_profile,
            "has_openai_api_key": self.has_openai_api_key,
        }


def load_settings() -> MusicAgentSettings:
    """Load settings from environment variables without requiring a .env file."""

    return MusicAgentSettings(
        input_mode=parse_input_mode(os.environ.get("MUSICAGENT_INPUT_MODE", "copy")),
        llm_provider=os.environ.get("MUSICAGENT_LLM_PROVIDER", "stub"),
        deployment_profile=parse_deployment_profile(
            os.environ.get("MUSICAGENT_DEPLOYMENT_PROFILE", "app")
        ),
        has_openai_api_key=bool(os.environ.get("OPENAI_API_KEY")),
    )


def parse_input_mode(value: str) -> InputModeSetting:
    if value == "copy":
        return "copy"
    if value == "reference":
        return "reference"
    raise ValueError(f"Unsupported input mode: {value}")


def parse_deployment_profile(value: str) -> DeploymentProfileSetting:
    if value == "app":
        return "app"
    if value == "crew":
        return "crew"
    if value == "agent":
        return "agent"
    raise ValueError(f"Unsupported deployment profile: {value}")
