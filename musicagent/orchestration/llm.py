"""LLM client abstractions and provider factory for orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from musicagent.config import MusicAgentSettings


class ProviderConfigurationError(ValueError):
    """Raised when a selected model provider is missing required configuration."""


class StubLLMClient:
    """Deterministic LLM test double used for offline development and tests."""

    required_environment_variables: tuple[str, ...] = ()

    def complete(self, agent_id: str, prompt: str) -> str:
        return f"Stub response for {agent_id}: {prompt}"


@dataclass(frozen=True)
class LangChainOpenAICompatibleLLMClient:
    """OpenAI-compatible LangChain client descriptor."""

    model: str
    base_url: str | None = None

    @property
    def required_environment_variables(self) -> tuple[str, ...]:
        return ("OPENAI_API_KEY", "MUSICAGENT_MODEL")

    def complete(self, agent_id: str, prompt: str) -> str:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=self.model, base_url=self.base_url)
        prompt_text = chr(10).join([f"Agent: {agent_id}", "", prompt])
        response = llm.invoke(prompt_text)
        return str(response.content)


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

    def complete(self, agent_id: str, prompt: str) -> str:
        from langchain_openai import AzureChatOpenAI

        llm = AzureChatOpenAI(
            azure_endpoint=self.endpoint,
            azure_deployment=self.deployment,
            api_version=self.api_version,
        )
        prompt_text = chr(10).join([f"Agent: {agent_id}", "", prompt])
        response = llm.invoke(prompt_text)
        return str(response.content)


def create_llm_client(
    settings: MusicAgentSettings, environ: Mapping[str, str] | None = None
) -> StubLLMClient | LangChainOpenAICompatibleLLMClient | AzureOpenAILLMClient:
    """Create an LLM client for the configured provider without making network calls."""

    env = environ or {}
    if settings.llm_provider == "stub":
        return StubLLMClient()
    if settings.llm_provider in {"openai", "openai-compatible"}:
        require_env(env, ("OPENAI_API_KEY", "MUSICAGENT_MODEL"), settings.llm_provider)
        return LangChainOpenAICompatibleLLMClient(
            model=env["MUSICAGENT_MODEL"],
            base_url=env.get("MUSICAGENT_OPENAI_BASE_URL"),
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


def require_env(env: Mapping[str, str], names: tuple[str, ...], provider: str) -> None:
    missing = tuple(name for name in names if not env.get(name))
    if missing:
        joined = ", ".join(missing)
        raise ProviderConfigurationError(
            f"LLM provider '{provider}' is missing required environment variables: {joined}"
        )
