"""LLM client abstractions and provider factory for orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol

from musicagent.config import MusicAgentSettings


class ProviderConfigurationError(ValueError):
    """Raised when a selected model provider is missing required configuration."""


class LLMClient(Protocol):
    """Protocol for model clients used by agent runners."""

    @property
    def required_environment_variables(self) -> tuple[str, ...]:
        """Return provider-specific environment variable names."""

    def complete(self, agent_id: str, prompt: str, model: str | None = None) -> str:
        """Return model output for an agent prompt."""


@dataclass(frozen=True)
class AgentModelRouter:
    """Resolve which model should serve each agent request."""

    default_model: str | None = None
    low_resource_model: str | None = None
    use_low_resource_model: bool = False
    agent_model_overrides: Mapping[str, str] = field(default_factory=dict)

    def model_for(self, agent_id: str) -> str | None:
        """Return the configured model for an agent, if any."""

        if self.use_low_resource_model and self.low_resource_model:
            return self.low_resource_model
        return self.agent_model_overrides.get(agent_id, self.default_model)


class StubLLMClient:
    """Deterministic LLM test double used for offline development and tests."""

    required_environment_variables: tuple[str, ...] = ()

    def complete(self, agent_id: str, prompt: str, model: str | None = None) -> str:
        model_suffix = f" using {model}" if model else ""
        return f"Stub response for {agent_id}{model_suffix}: {prompt}"


@dataclass(frozen=True)
class LangChainOpenAICompatibleLLMClient:
    """OpenAI-compatible LangChain client descriptor."""

    model: str
    base_url: str | None = None

    @property
    def required_environment_variables(self) -> tuple[str, ...]:
        return ("OPENAI_API_KEY", "MUSICAGENT_MODEL")

    def complete(self, agent_id: str, prompt: str, model: str | None = None) -> str:
        from openai import OpenAI

        selected_model = model or self.model
        client = OpenAI(base_url=self.base_url) if self.base_url else OpenAI()
        response = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": format_agent_prompt(agent_id, prompt)}],
        )
        return extract_chat_completion_content(response)


@dataclass(frozen=True)
class LangChainOpenAILLMClient(LangChainOpenAICompatibleLLMClient):
    """Backward-compatible OpenAI provider alias."""


@dataclass(frozen=True)
class AzureOpenAILLMClient:
    """Azure OpenAI LangChain client descriptor."""

    endpoint: str
    deployment: str
    api_version: str

    @property
    def required_environment_variables(self) -> tuple[str, ...]:
        return (
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_OPENAI_API_VERSION",
        )

    def complete(self, agent_id: str, prompt: str, model: str | None = None) -> str:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_version=self.api_version,
        )
        response = client.chat.completions.create(
            model=model or self.deployment,
            messages=[{"role": "user", "content": format_agent_prompt(agent_id, prompt)}],
        )
        return extract_chat_completion_content(response)


def format_agent_prompt(agent_id: str, prompt: str) -> str:
    """Return the common text prompt sent to chat-completion providers."""

    return chr(10).join([f"Agent: {agent_id}", "", prompt])


def extract_chat_completion_content(response: Any) -> str:
    """Extract text content from an OpenAI chat completion response."""

    choices = getattr(response, "choices", None)
    if not choices:
        return ""
    message = choices[0].message
    content = getattr(message, "content", "")
    if content is None:
        return ""
    return str(content)


def create_agent_model_router(settings: MusicAgentSettings) -> AgentModelRouter:
    """Create a per-agent model router from runtime settings."""

    return AgentModelRouter(
        default_model=settings.llm_model,
        low_resource_model=settings.low_resource_model,
        use_low_resource_model=settings.use_low_resource_model,
        agent_model_overrides=settings.agent_model_overrides,
    )


def create_llm_client(
    settings: MusicAgentSettings, environ: Mapping[str, str] | None = None
) -> LLMClient:
    """Create an LLM client for the configured provider without making network calls."""

    env = environ or {}
    if settings.llm_provider == "stub":
        return StubLLMClient()
    if settings.llm_provider in {"openai", "openai-compatible"}:
        model = settings.llm_model or env.get("MUSICAGENT_MODEL")
        require_openai_compatible_config(settings.llm_provider, env, model)
        return LangChainOpenAICompatibleLLMClient(
            model=required_setting(model, "MUSICAGENT_MODEL", settings.llm_provider),
            base_url=settings.llm_base_url or env.get("MUSICAGENT_OPENAI_BASE_URL"),
        )
    if settings.llm_provider == "azure-openai":
        require_env(
            env,
            (
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_OPENAI_DEPLOYMENT",
                "AZURE_OPENAI_API_VERSION",
            ),
            settings.llm_provider,
        )
        return AzureOpenAILLMClient(
            endpoint=env["AZURE_OPENAI_ENDPOINT"],
            deployment=env["AZURE_OPENAI_DEPLOYMENT"],
            api_version=env["AZURE_OPENAI_API_VERSION"],
        )
    raise ProviderConfigurationError(f"Unsupported LLM provider: {settings.llm_provider}")


def require_openai_compatible_config(
    provider: str, env: Mapping[str, str], model: str | None
) -> None:
    missing = []
    if not env.get("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if not model:
        missing.append("MUSICAGENT_MODEL")
    if missing:
        joined = ", ".join(missing)
        raise ProviderConfigurationError(
            f"LLM provider '{provider}' is missing required environment variables: {joined}"
        )


def required_setting(value: str | None, name: str, provider: str) -> str:
    if value:
        return value
    raise ProviderConfigurationError(
        f"LLM provider '{provider}' is missing required environment variables: {name}"
    )


def require_env(env: Mapping[str, str], names: tuple[str, ...], provider: str) -> None:
    missing = tuple(name for name in names if not env.get(name))
    if missing:
        joined = ", ".join(missing)
        raise ProviderConfigurationError(
            f"LLM provider '{provider}' is missing required environment variables: {joined}"
        )
