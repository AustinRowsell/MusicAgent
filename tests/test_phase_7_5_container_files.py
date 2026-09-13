from pathlib import Path

REQUIRED_DOCKERIGNORE_PATTERNS = {
    ".env",
    ".git",
    ".venv",
    ".idea",
    "outputs/",
    "__pycache__/",
    ".pytest_cache/",
}


def test_dockerignore_excludes_secrets_and_generated_artifacts():
    content = Path(".dockerignore").read_text().splitlines()

    for pattern in REQUIRED_DOCKERIGNORE_PATTERNS:
        assert pattern in content


def test_dockerfile_uses_supported_python_and_non_root_runtime():
    content = Path("Dockerfile").read_text()

    assert "# syntax=docker/dockerfile:1.7" in content
    assert "python:3.14" in content
    assert "--mount=type=secret,id=musicagent_local_ca_bundle" in content
    assert "update-ca-certificates" in content
    assert "uv pip install --system --system-certs ." in content
    assert "USER musicagent" in content
    assert "EXPOSE 8000" in content
    assert "CMD" in content


def test_env_example_exists_without_secret_values():
    content = Path(".env.example").read_text()

    assert "OPENAI_API_KEY=" in content
    assert "MUSICAGENT_LLM_PROVIDER=stub" in content
    assert "MUSICAGENT_OPENAI_BASE_URL=http://ollama:11434/v1" in content
    assert "MUSICAGENT_AGENT_MODEL_LYRICIST_POET=mistral-nemo:12b" in content
    assert "MUSICAGENT_AGENT_MODEL_TOPLINER=mistral-nemo:12b" in content
    assert "MUSICAGENT_LOW_RESOURCE_MODEL=llama3.2:3b" in content
    assert ".env.local-llm-profiles.example" in content
    assert "secret" not in content.lower().replace("no secrets", "").replace(
        "not a real secret", ""
    )


def test_local_llm_profiles_example_covers_workstation_tiers_without_real_secrets():
    content = Path(".env.local-llm-profiles.example").read_text()

    for profile in (
        "Profile 0: Offline/stub baseline",
        "Profile 1: Minimum Docker local LLM",
        "Profile 2: Standard laptop local LLM",
        "Profile 3: Creative songwriter workstation",
        "Profile 4: Quality workstation",
        "Profile 5: Highest reasonable home setup",
    ):
        assert profile in content

    for model in (
        "llama3.2:3b",
        "llama3.1:8b",
        "mistral-nemo:12b",
        "qwen2.5:14b",
        "qwen2.5:32b",
        "llama3.1:70b",
    ):
        assert model in content

    for runtime_url in (
        "http://ollama:11434/v1",
        "http://localai:8080/v1",
        "http://llama-cpp:8080/v1",
        "http://vllm:8000/v1",
    ):
        assert runtime_url in content

    assert "sk-" not in content
    assert "bearer " not in content.lower()
    assert "super-secret" not in content.lower()
