"""Non-secret diagnostics for LLM configuration and local runtimes."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict

from musicagent.config import MusicAgentSettings
from musicagent.orchestration.llm import ProviderConfigurationError, create_llm_client


class UrlOpen(Protocol):
    """Minimal URL opener protocol used by runtime diagnostics."""

    def __call__(self, request: urllib.request.Request, *, timeout: float) -> Any:
        """Open a request with a timeout."""


class ModelInventoryError(RuntimeError):
    """Raised when a local runtime model inventory cannot be read."""


class ConfigDiagnostic(BaseModel):
    """Non-secret LLM configuration diagnostic output."""

    model_config = ConfigDict(frozen=True)

    provider: str
    default_model: str | None
    low_resource_model: str | None
    use_low_resource_model: bool
    agent_model_overrides: dict[str, str]
    has_base_url: bool
    base_url_host: str | None
    configured_models: tuple[str, ...]
    has_openai_api_key: bool


class ModelAvailabilityDiagnostic(BaseModel):
    """Safe report for configured-vs-available local runtime models."""

    model_config = ConfigDict(frozen=True)

    checked: bool
    ok: bool
    configured_models: tuple[str, ...] = ()
    available_models: tuple[str, ...] = ()
    missing_models: tuple[str, ...] = ()
    suggested_pull_commands: tuple[str, ...] = ()
    message: str = ""


class ReachabilityDiagnostic(BaseModel):
    """Safe report for an LLM completion reachability check."""

    model_config = ConfigDict(frozen=True)

    checked: bool
    ok: bool
    provider: str
    model: str | None = None
    message: str = ""


class RuntimeAlternative(BaseModel):
    """Documented non-Ollama runtime alternative."""

    model_config = ConfigDict(frozen=True)

    name: str
    status: str
    use_when: str


class LLMDiagnosticReport(BaseModel):
    """Combined non-secret local LLM diagnostic report."""

    model_config = ConfigDict(frozen=True)

    config: ConfigDiagnostic
    reachability: ReachabilityDiagnostic | None = None
    model_availability: ModelAvailabilityDiagnostic | None = None


def build_config_diagnostic(settings: MusicAgentSettings) -> ConfigDiagnostic:
    """Build non-secret provider/model diagnostics from settings."""

    return ConfigDiagnostic(
        provider=settings.llm_provider,
        default_model=settings.llm_model,
        low_resource_model=settings.low_resource_model,
        use_low_resource_model=settings.use_low_resource_model,
        agent_model_overrides=dict(settings.agent_model_overrides),
        has_base_url=settings.llm_base_url is not None,
        base_url_host=redacted_base_url_host(settings.llm_base_url),
        configured_models=configured_model_names(settings),
        has_openai_api_key=settings.has_openai_api_key,
    )


def configured_model_names(settings: MusicAgentSettings) -> tuple[str, ...]:
    """Return all configured model names in deterministic order without duplicates."""

    models: list[str] = []
    for model in (
        settings.llm_model,
        settings.low_resource_model,
        *settings.agent_model_overrides.values(),
    ):
        if model and model not in models:
            models.append(model)
    return tuple(models)


def redacted_base_url_host(base_url: str | None) -> str | None:
    """Return a safe host[:port] value for a base URL without user info or paths."""

    if base_url is None:
        return None
    parsed = urllib.parse.urlparse(base_url)
    if not parsed.hostname:
        return None
    if parsed.port is None:
        return parsed.hostname
    return f"{parsed.hostname}:{parsed.port}"


def check_llm_reachability(
    settings: MusicAgentSettings,
    environ: Mapping[str, str],
    prompt: str = "Return the word ok.",
) -> ReachabilityDiagnostic:
    """Run a tiny provider reachability check without exposing credentials."""

    if settings.llm_provider == "stub":
        return ReachabilityDiagnostic(
            checked=True,
            ok=True,
            provider=settings.llm_provider,
            model=settings.llm_model,
            message="stub provider is available without network access",
        )

    try:
        client = create_llm_client(settings, environ)
        response = client.complete("diagnostic", prompt, model=settings.llm_model)
    except ProviderConfigurationError as error:
        return ReachabilityDiagnostic(
            checked=True,
            ok=False,
            provider=settings.llm_provider,
            model=settings.llm_model,
            message=str(error),
        )
    except (OSError, RuntimeError, ValueError, urllib.error.URLError) as error:
        return ReachabilityDiagnostic(
            checked=True,
            ok=False,
            provider=settings.llm_provider,
            model=settings.llm_model,
            message=f"LLM reachability check failed: {type(error).__name__}",
        )

    if not response.strip():
        return ReachabilityDiagnostic(
            checked=True,
            ok=False,
            provider=settings.llm_provider,
            model=settings.llm_model,
            message="LLM returned an empty response",
        )
    return ReachabilityDiagnostic(
        checked=True,
        ok=True,
        provider=settings.llm_provider,
        model=settings.llm_model,
        message="LLM returned a response",
    )


def check_model_availability(
    settings: MusicAgentSettings,
    environ: Mapping[str, str],
    urlopen: UrlOpen | None = None,
    timeout_seconds: float = 5.0,
) -> ModelAvailabilityDiagnostic:
    """Check whether all configured models are available in the local runtime."""

    configured = configured_model_names(settings)
    if settings.llm_provider == "stub":
        return ModelAvailabilityDiagnostic(
            checked=False,
            ok=True,
            configured_models=configured,
            message="stub provider has no external model inventory",
        )
    if settings.llm_provider not in {"openai", "openai-compatible"}:
        return ModelAvailabilityDiagnostic(
            checked=False,
            ok=True,
            configured_models=configured,
            message=f"model inventory is not implemented for provider '{settings.llm_provider}'",
        )
    if not settings.llm_base_url:
        return ModelAvailabilityDiagnostic(
            checked=True,
            ok=False,
            configured_models=configured,
            message="MUSICAGENT_OPENAI_BASE_URL is required for model availability checks",
        )

    try:
        available = list_openai_compatible_models(
            settings.llm_base_url,
            api_key=environ.get("OPENAI_API_KEY"),
            urlopen=urlopen or open_url,
            timeout_seconds=timeout_seconds,
        )
    except ModelInventoryError as error:
        return ModelAvailabilityDiagnostic(
            checked=True,
            ok=False,
            configured_models=configured,
            message=f"model availability check failed: {error}",
        )

    missing = tuple(model for model in configured if model not in available)
    return ModelAvailabilityDiagnostic(
        checked=True,
        ok=not missing,
        configured_models=configured,
        available_models=available,
        missing_models=missing,
        suggested_pull_commands=tuple(
            f"./scripts/docker-local-llm-pull.sh {model}" for model in missing
        ),
        message="all configured models are available"
        if not missing
        else "missing configured models",
    )


def list_openai_compatible_models(
    base_url: str,
    api_key: str | None,
    urlopen: UrlOpen | None = None,
    timeout_seconds: float = 5.0,
) -> tuple[str, ...]:
    """List model names from OpenAI-compatible or Ollama model endpoints."""

    opener = urlopen or open_url
    errors: list[Exception] = []
    for url in model_inventory_urls(base_url):
        try:
            payload = fetch_json(
                url, api_key=api_key, urlopen=opener, timeout_seconds=timeout_seconds
            )
            models = parse_model_inventory(payload)
            if models:
                return models
        except (
            OSError,
            urllib.error.URLError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ) as error:
            errors.append(error)
    if errors:
        raise ModelInventoryError(type(errors[-1]).__name__) from errors[-1]
    return ()


def model_inventory_urls(base_url: str) -> tuple[str, ...]:
    """Return candidate safe model-inventory URLs for compatible runtimes."""

    normalized = base_url.rstrip("/")
    urls = [f"{normalized}/models"]
    parsed = urllib.parse.urlparse(normalized)
    if parsed.path.rstrip("/") == "/v1":
        root = parsed._replace(path="", params="", query="", fragment="").geturl().rstrip("/")
        urls.append(f"{root}/api/tags")
    return tuple(urls)


def open_url(request: urllib.request.Request, *, timeout: float) -> Any:
    """Open a URL request with the exact signature diagnostics need."""

    return urllib.request.urlopen(request, timeout=timeout)


def fetch_json(
    url: str,
    api_key: str | None,
    urlopen: UrlOpen,
    timeout_seconds: float,
) -> object:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    request = urllib.request.Request(url, headers=headers)
    with urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_model_inventory(payload: object) -> tuple[str, ...]:
    """Parse OpenAI /v1/models or Ollama /api/tags model inventory payloads."""

    if not isinstance(payload, dict):
        raise TypeError("model inventory response must be an object")

    names: list[str] = []
    data = payload.get("data")
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                names.append(item["id"])

    models = payload.get("models")
    if isinstance(models, list):
        for item in models:
            if isinstance(item, dict) and isinstance(item.get("name"), str):
                names.append(item["name"])

    return tuple(dict.fromkeys(names))


def runtime_alternatives() -> tuple[RuntimeAlternative, ...]:
    """Return the planned runtime evaluation order for non-Ollama options."""

    return (
        RuntimeAlternative(
            name="Ollama",
            status="implemented-first",
            use_when="default Dockerised local LLM runtime",
        ),
        RuntimeAlternative(
            name="LocalAI",
            status="future-option",
            use_when="evaluate if Ollama lacks backend flexibility or model support",
        ),
        RuntimeAlternative(
            name="llama.cpp server",
            status="future-option",
            use_when="evaluate if direct GGUF/CPU control is needed",
        ),
        RuntimeAlternative(
            name="vLLM",
            status="future-option",
            use_when="evaluate for GPU workstation or server throughput",
        ),
    )
