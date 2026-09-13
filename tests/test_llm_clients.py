import sys
from pathlib import Path
from types import SimpleNamespace

from musicagent.orchestration.llm import LangChainOpenAILLMClient, StubLLMClient


def test_stub_llm_client_returns_deterministic_response():
    response = StubLLMClient().complete("groove_architect", "make drums")

    assert "groove_architect" in response
    assert "make drums" in response


def test_langchain_client_declares_required_environment_variables():
    client = LangChainOpenAILLMClient(model="test-model")

    assert client.required_environment_variables == ("OPENAI_API_KEY", "MUSICAGENT_MODEL")


def test_openai_compatible_client_uses_openai_sdk_without_langchain_import(monkeypatch):
    sys.modules.pop("langchain_openai", None)
    calls: list[tuple[str, str | None, list[dict[str, str]]]] = []

    class FakeOpenAI:
        def __init__(self, base_url: str | None = None) -> None:
            self.base_url = base_url
            self.chat = self
            self.completions = self

        def create(self, model: str, messages: list[dict[str, str]]) -> object:
            calls.append((model, self.base_url, messages))
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="model response"))]
            )

    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)

    response = LangChainOpenAILLMClient(
        model="llama3.2:3b", base_url="http://ollama:11434/v1"
    ).complete("lyricist_poet", "write a chorus")

    assert response == "model response"
    assert calls == [
        (
            "llama3.2:3b",
            "http://ollama:11434/v1",
            [{"role": "user", "content": "Agent: lyricist_poet\n\nwrite a chorus"}],
        )
    ]
    assert "langchain_openai" not in sys.modules


def test_project_declares_pydantic_v2_runtime_requirement():
    content = Path("pyproject.toml").read_text()

    assert '"pydantic>=2.12.5"' in content
    assert '"langchain-openai"' in content
