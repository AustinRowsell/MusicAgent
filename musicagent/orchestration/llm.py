"""LLM client abstractions for orchestration."""

from __future__ import annotations

from dataclasses import dataclass


class StubLLMClient:
    """Deterministic LLM test double used for offline development and tests."""

    def complete(self, agent_id: str, prompt: str) -> str:
        return f"Stub response for {agent_id}: {prompt}"


@dataclass(frozen=True)
class LangChainOpenAILLMClient:
    """Thin descriptor for future LangChain OpenAI-backed execution."""

    model: str

    @property
    def required_environment_variables(self) -> tuple[str, ...]:
        return ("OPENAI_API_KEY",)

    def complete(self, agent_id: str, prompt: str) -> str:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=self.model)
        prompt_text = chr(10).join([f"Agent: {agent_id}", "", prompt])
        response = llm.invoke(prompt_text)
        return str(response.content)
