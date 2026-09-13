import pytest
from musicagent.config import MusicAgentSettings
from musicagent.orchestration.llm import (
    AzureOpenAILLMClient,
    LangChainOpenAICompatibleLLMClient,
    ProviderConfigurationError,
    StubLLMClient,
    create_llm_client,
)


def test_stub_provider_requires_no_credentials():
    client = create_llm_client(MusicAgentSettings(llm_provider="stub"), environ={})

    assert isinstance(client, StubLLMClient)
    assert client.complete("agent", "prompt") == "Stub response for agent: prompt"


def test_openai_compatible_provider_reports_missing_config_without_secret_values():
    settings = MusicAgentSettings(llm_provider="openai-compatible")

    with pytest.raises(ProviderConfigurationError) as error:
        create_llm_client(settings, environ={"OPENAI_API_KEY": "secret-value"})

    message = str(error.value)
    assert "MUSICAGENT_MODEL" in message
    assert "secret-value" not in message


def test_openai_compatible_provider_uses_configured_base_url_without_network_call():
    settings = MusicAgentSettings(llm_provider="openai-compatible")

    client = create_llm_client(
        settings,
        environ={
            "OPENAI_API_KEY": "secret-value",
            "MUSICAGENT_MODEL": "test-model",
            "MUSICAGENT_OPENAI_BASE_URL": "https://llm.example.test/v1",
        },
    )

    assert isinstance(client, LangChainOpenAICompatibleLLMClient)
    assert client.model == "test-model"
    assert client.base_url == "https://llm.example.test/v1"


def test_azure_provider_reports_required_environment_names_without_values():
    settings = MusicAgentSettings(llm_provider="azure-openai")

    with pytest.raises(ProviderConfigurationError) as error:
        create_llm_client(settings, environ={"AZURE_OPENAI_API_KEY": "secret-value"})

    message = str(error.value)
    assert "AZURE_OPENAI_ENDPOINT" in message
    assert "AZURE_OPENAI_DEPLOYMENT" in message
    assert "secret-value" not in message


def test_azure_provider_can_be_constructed_without_network_call():
    settings = MusicAgentSettings(llm_provider="azure-openai")

    client = create_llm_client(
        settings,
        environ={
            "AZURE_OPENAI_API_KEY": "secret-value",
            "AZURE_OPENAI_ENDPOINT": "https://azure.example.test",
            "AZURE_OPENAI_DEPLOYMENT": "music-agent",
            "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        },
    )

    assert isinstance(client, AzureOpenAILLMClient)
    assert client.endpoint == "https://azure.example.test"
    assert client.deployment == "music-agent"
