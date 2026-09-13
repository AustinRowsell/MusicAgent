from pathlib import Path

import yaml


def test_compose_local_llm_profile_defines_ollama_runtime_and_model_volume():
    compose = yaml.safe_load(Path("compose.yaml").read_text())
    services = compose["services"]

    assert services["ollama"]["profiles"] == ["local-llm"]
    assert services["ollama"]["image"] == "ollama/ollama:latest"
    assert "environment" not in services["ollama"]
    assert "ollama-models:/root/.ollama" in services["ollama"]["volumes"]
    assert all("certs" not in volume for volume in services["ollama"]["volumes"])
    assert "ollama-models" in compose["volumes"]


def test_optional_local_cert_compose_override_uses_build_secret_and_mounts_certs_only_for_ollama():
    compose = yaml.safe_load(Path("compose.local-certs.yaml").read_text())
    services = compose["services"]
    ollama = services["ollama"]

    for service_name, service in services.items():
        if service_name == "ollama":
            continue

        assert service["build"]["context"] == "."
        assert service["build"]["secrets"] == [
            {
                "source": "musicagent_local_ca_bundle",
                "target": "musicagent_local_ca_bundle",
            }
        ]

    assert compose["secrets"]["musicagent_local_ca_bundle"] == {
        "file": "./certs/musicagent-local-ca-bundle.pem"
    }
    assert ollama["environment"]["SSL_CERT_DIR"] == (
        "/etc/ssl/certs:/usr/local/share/ca-certificates/musicagent"
    )
    assert ollama["volumes"] == [
        "./certs:/usr/local/share/ca-certificates/musicagent:ro"
    ]


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


def test_compose_does_not_define_dns_dependent_ollama_pull_service():
    compose = yaml.safe_load(Path("compose.yaml").read_text())

    assert "ollama-pull" not in compose["services"]
