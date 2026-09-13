from pathlib import Path


def test_readme_documents_install_and_common_run_commands():
    content = Path("README.md").read_text()

    for command in (
        "./scripts/install.sh",
        "./scripts/local-cli.sh crews",
        "./scripts/local-web.sh",
        "./scripts/docker-cli.sh crews",
        "./scripts/docker-create.sh --name electronic-example",
        "./scripts/docker-web.sh",
        "./scripts/docker-crew.sh electronic",
        "./scripts/docker-agent.sh groove",
        "./scripts/docker-local-llm-pull.sh llama3.1:8b",
        "./scripts/docker-local-llm-pull.sh mistral-nemo:12b",
        "./scripts/docker-local-llm-web.sh",
        "./scripts/docker-local-llm-create.sh --name local-llm-example",
        "./scripts/local-cli.sh config",
        "./scripts/local-cli.sh llm-runtimes",
        "./scripts/docker-local-llm-check.sh",
    ):
        assert command in content


def test_readme_documents_outputs_and_no_secret_policy():
    content = Path("README.md").read_text().lower()

    assert "outputs/" in content
    assert ".env.example" in content
    assert ".env.local-llm-profiles.example" in content
    assert "never commit real .env" in content
    assert "full_sketch.mid" in content
    assert "sk-" not in content
    assert "secret-value" not in content


def test_readme_documents_dockerised_local_llm_model_routing():
    content = Path("README.md").read_text()

    assert "Ollama is the first supported container runtime, but Ollama is not the model" in content
    assert "MUSICAGENT_MODEL=llama3.1:8b" in content
    assert "MUSICAGENT_AGENT_MODEL_LYRICIST_POET=mistral-nemo:12b" in content
    assert "MUSICAGENT_AGENT_MODEL_TOPLINER=mistral-nemo:12b" in content
    assert "MUSICAGENT_AGENT_MODEL_CYBER_CRITIC=qwen2.5:14b" in content
    assert "MUSICAGENT_LOW_RESOURCE_MODEL=llama3.2:3b" in content
    assert "MUSICAGENT_USE_LOW_RESOURCE_MODEL=true" in content
