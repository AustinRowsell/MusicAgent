from musicagent.cli import app
from typer.testing import CliRunner

runner = CliRunner()


def test_config_command_prints_non_secret_model_diagnostics(monkeypatch):
    monkeypatch.setenv("MUSICAGENT_LLM_PROVIDER", "openai-compatible")
    monkeypatch.setenv("MUSICAGENT_MODEL", "llama3.1:8b")
    monkeypatch.setenv("MUSICAGENT_OPENAI_BASE_URL", "http://user:password@ollama:11434/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "super-secret-token")
    monkeypatch.setenv("MUSICAGENT_AGENT_MODEL_LYRICIST_POET", "mistral-nemo:12b")

    result = runner.invoke(app, ["config"])

    assert result.exit_code == 0
    assert '"provider": "openai-compatible"' in result.stdout
    assert '"base_url_host": "ollama:11434"' in result.stdout
    assert "mistral-nemo:12b" in result.stdout
    assert "super-secret-token" not in result.stdout
    assert "password" not in result.stdout


def test_llm_check_stub_provider_succeeds_without_network():
    result = runner.invoke(app, ["llm-check"])

    assert result.exit_code == 0
    assert '"provider": "stub"' in result.stdout
    assert "stub provider is available" in result.stdout


def test_llm_check_reports_missing_non_stub_configuration_without_secret_values(monkeypatch):
    monkeypatch.setenv("MUSICAGENT_LLM_PROVIDER", "openai-compatible")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MUSICAGENT_MODEL", raising=False)

    result = runner.invoke(app, ["llm-check", "--no-models"])

    assert result.exit_code == 1
    assert "OPENAI_API_KEY" in result.stdout
    assert "MUSICAGENT_MODEL" in result.stdout
    assert "secret" not in result.stdout.lower()


def test_llm_runtimes_lists_non_ollama_alternatives():
    result = runner.invoke(app, ["llm-runtimes"])

    assert result.exit_code == 0
    assert "Ollama" in result.stdout
    assert "LocalAI" in result.stdout
    assert "llama.cpp server" in result.stdout
    assert "vLLM" in result.stdout
