from pathlib import Path

import yaml


def test_compose_local_llm_profile_defines_ollama_runtime_and_model_volume():
    compose = yaml.safe_load(Path("compose.yaml").read_text())
    services = compose["services"]

    assert services["ollama"]["profiles"] == ["local-llm"]
    assert services["ollama"]["image"] == "ollama/ollama:latest"
    assert "ollama-models:/root/.ollama" in services["ollama"]["volumes"]
    assert "ollama-models" in compose["volumes"]


def test_compose_local_llm_services_use_container_endpoint_and_model_routing():
    compose = yaml.safe_load(Path("compose.yaml").read_text())

    for service_name in ("musicagent-local-llm-cli", "musicagent-local-llm-web"):
        service = compose["services"][service_name]
        environment = service["environment"]

        assert service["profiles"] == ["local-llm"]
        assert service["depends_on"] == ["ollama"]
        assert environment["MUSICAGENT_LLM_PROVIDER"] == "openai-compatible"
        assert environment["MUSICAGENT_MODEL"] == "${MUSICAGENT_MODEL:-llama3.1:8b}"
        assert environment["MUSICAGENT_OPENAI_BASE_URL"] == "http://ollama:11434/v1"
        assert environment["MUSICAGENT_LOW_RESOURCE_MODEL"] == (
            "${MUSICAGENT_LOW_RESOURCE_MODEL:-llama3.2:3b}"
        )
        assert environment["MUSICAGENT_AGENT_MODEL_LYRICIST_POET"] == (
            "${MUSICAGENT_AGENT_MODEL_LYRICIST_POET:-mistral-nemo:12b}"
        )
        assert environment["MUSICAGENT_AGENT_MODEL_TOPLINER"] == (
            "${MUSICAGENT_AGENT_MODEL_TOPLINER:-mistral-nemo:12b}"
        )
        assert environment["MUSICAGENT_AGENT_MODEL_CYBER_CRITIC"] == (
            "${MUSICAGENT_AGENT_MODEL_CYBER_CRITIC:-qwen2.5:14b}"
        )
        assert environment["OPENAI_API_KEY"] == "${OPENAI_API_KEY:-ollama-local-placeholder}"


def test_compose_ollama_pull_uses_selected_model_default():
    compose = yaml.safe_load(Path("compose.yaml").read_text())
    ollama_pull = compose["services"]["ollama-pull"]

    assert ollama_pull["profiles"] == ["local-llm"]
    assert ollama_pull["depends_on"] == ["ollama"]
    assert ollama_pull["environment"]["OLLAMA_HOST"] == "http://ollama:11434"
    assert ollama_pull["command"] == ["${MUSICAGENT_MODEL:-llama3.1:8b}"]
