from musicagent.orchestration.llm import LangChainOpenAILLMClient, StubLLMClient


def test_stub_llm_client_returns_deterministic_response():
    response = StubLLMClient().complete("groove_architect", "make drums")

    assert "groove_architect" in response
    assert "make drums" in response


def test_langchain_client_declares_required_environment_variables():
    client = LangChainOpenAILLMClient(model="test-model")

    assert client.required_environment_variables == ("OPENAI_API_KEY", "MUSICAGENT_MODEL")
