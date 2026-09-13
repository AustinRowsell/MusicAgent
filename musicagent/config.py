"""Runtime configuration contracts for answered product decisions."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

InputModeSetting = Literal["copy", "reference"]
DeploymentProfileSetting = Literal["app", "crew", "agent"]

_AGENT_MODEL_PREFIX = "MUSICAGENT_AGENT_MODEL_"


class MusicAgentSettings(BaseModel):
    """Typed configuration for decision-gated runtime behaviour."""

    model_config = ConfigDict(frozen=True)

    interface_mode: Literal["both"] = "both"
    midi_metadata_mode: Literal["names_and_general_midi"] = "names_and_general_midi"
    input_mode: InputModeSetting = "copy"
    audio_mode: Literal["metadata_only"] = "metadata_only"
    llm_provider: str = "stub"
    llm_model: str | None = None
    llm_base_url: str | None = None
    low_resource_model: str | None = None
    use_low_resource_model: bool = False
    agent_model_overrides: dict[str, str] = Field(default_factory=dict)
    model_provider_mode: Literal["fully_pluggable"] = "fully_pluggable"
    output_path_mode: Literal["relative_and_absolute"] = "relative_and_absolute"
    electronic_structure_mode: Literal["style_pack"] = "style_pack"
    acoustic_accompaniment_default: Literal["guitar_first"] = "guitar_first"
    deployment_profile: DeploymentProfileSetting = "app"
    has_openai_api_key: bool = False

    def public_snapshot(self) -> dict[str, str | bool | dict[str, str] | None]:
        """Return non-secret settings for diagnostics/manifests."""

        return {
            "interface_mode": self.interface_mode,
            "midi_metadata_mode": self.midi_metadata_mode,
            "input_mode": self.input_mode,
            "audio_mode": self.audio_mode,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "has_llm_base_url": self.llm_base_url is not None,
            "low_resource_model": self.low_resource_model,
            "use_low_resource_model": self.use_low_resource_model,
            "agent_model_overrides": dict(self.agent_model_overrides),
            "model_provider_mode": self.model_provider_mode,
            "output_path_mode": self.output_path_mode,
            "electronic_structure_mode": self.electronic_structure_mode,
            "acoustic_accompaniment_default": self.acoustic_accompaniment_default,
            "deployment_profile": self.deployment_profile,
            "has_openai_api_key": self.has_openai_api_key,
        }


def load_settings(environ: Mapping[str, str] | None = None) -> MusicAgentSettings:
    """Load settings from environment variables without requiring a .env file."""

    env = os.environ if environ is None else environ
    return MusicAgentSettings(
        input_mode=parse_input_mode(env.get("MUSICAGENT_INPUT_MODE", "copy")),
        llm_provider=env.get("MUSICAGENT_LLM_PROVIDER", "stub"),
        llm_model=empty_to_none(env.get("MUSICAGENT_MODEL")),
        llm_base_url=empty_to_none(env.get("MUSICAGENT_OPENAI_BASE_URL")),
        low_resource_model=empty_to_none(env.get("MUSICAGENT_LOW_RESOURCE_MODEL")),
        use_low_resource_model=parse_bool(env.get("MUSICAGENT_USE_LOW_RESOURCE_MODEL", "false")),
        agent_model_overrides=load_agent_model_overrides(env),
        deployment_profile=parse_deployment_profile(
            env.get("MUSICAGENT_DEPLOYMENT_PROFILE", "app")
        ),
        has_openai_api_key=bool(env.get("OPENAI_API_KEY")),
    )


def empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return stripped


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off", ""}:
        return False
    raise ValueError(f"Unsupported boolean value: {value}")


def load_agent_model_overrides(environ: Mapping[str, str]) -> dict[str, str]:
    """Load per-agent model overrides from MUSICAGENT_AGENT_MODEL_<AGENT_ID>."""

    overrides: dict[str, str] = {}
    for name, value in environ.items():
        if not name.startswith(_AGENT_MODEL_PREFIX):
            continue
        model = empty_to_none(value)
        if model is None:
            continue
        agent_id = name.removeprefix(_AGENT_MODEL_PREFIX).lower()
        overrides[agent_id] = model
    return overrides


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
