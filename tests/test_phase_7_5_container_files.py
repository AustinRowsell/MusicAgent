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

    assert "python:3.13" in content or "python:3.12" in content
    assert "USER musicagent" in content
    assert "EXPOSE 8000" in content
    assert "CMD" in content


def test_env_example_exists_without_secret_values():
    content = Path(".env.example").read_text()

    assert "OPENAI_API_KEY=" in content
    assert "MUSICAGENT_LLM_PROVIDER=stub" in content
    assert "secret" not in content.lower().replace("no secrets", "")
