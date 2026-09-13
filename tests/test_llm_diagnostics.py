import json
from typing import Self

from musicagent.config import MusicAgentSettings
from musicagent.orchestration.diagnostics import (
    build_config_diagnostic,
    check_model_availability,
    list_openai_compatible_models,
    model_inventory_urls,
    runtime_alternatives,
)


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def test_config_diagnostic_redacts_base_url_credentials():
    settings = MusicAgentSettings(
        llm_provider="openai-compatible",
        llm_model="llama3.1:8b",
        llm_base_url="http://user:password@ollama:11434/v1",
        low_resource_model="llama3.2:3b",
        agent_model_overrides={"lyricist_poet": "mistral-nemo:12b"},
        has_openai_api_key=True,
    )

    diagnostic = build_config_diagnostic(settings)

    assert diagnostic.base_url_host == "ollama:11434"
    assert "password" not in str(diagnostic.model_dump())
    assert diagnostic.configured_models == (
        "llama3.1:8b",
        "llama3.2:3b",
        "mistral-nemo:12b",
    )


def test_model_inventory_urls_include_openai_and_ollama_tag_endpoints():
    assert model_inventory_urls("http://ollama:11434/v1") == (
        "http://ollama:11434/v1/models",
        "http://ollama:11434/api/tags",
    )


def test_list_openai_compatible_models_parses_openai_payload():
    def fake_urlopen(request: object, *, timeout: float) -> FakeResponse:
        return FakeResponse({"data": [{"id": "llama3.1:8b"}, {"id": "qwen2.5:14b"}]})

    assert list_openai_compatible_models(
        "http://ollama:11434/v1", api_key="placeholder", urlopen=fake_urlopen
    ) == ("llama3.1:8b", "qwen2.5:14b")


def test_model_availability_reports_missing_models_and_pull_commands():
    settings = MusicAgentSettings(
        llm_provider="openai-compatible",
        llm_model="llama3.1:8b",
        llm_base_url="http://ollama:11434/v1",
        agent_model_overrides={"lyricist_poet": "mistral-nemo:12b"},
    )

    def fake_urlopen(request: object, *, timeout: float) -> FakeResponse:
        return FakeResponse({"data": [{"id": "llama3.1:8b"}]})

    diagnostic = check_model_availability(
        settings, {"OPENAI_API_KEY": "placeholder"}, urlopen=fake_urlopen
    )

    assert diagnostic.checked is True
    assert diagnostic.ok is False
    assert diagnostic.missing_models == ("mistral-nemo:12b",)
    assert diagnostic.suggested_pull_commands == (
        "./scripts/docker-local-llm-pull.sh mistral-nemo:12b",
    )


def test_runtime_alternatives_document_non_ollama_options():
    names = [alternative.name for alternative in runtime_alternatives()]

    assert names[:4] == ["Ollama", "LocalAI", "llama.cpp server", "vLLM"]
