from musicagent.config import MusicAgentSettings, load_settings


def test_default_settings_codify_answered_decisions():
    settings = MusicAgentSettings()

    assert settings.interface_mode == "both"
    assert settings.midi_metadata_mode == "names_and_general_midi"
    assert settings.input_mode == "copy"
    assert settings.audio_mode == "metadata_only"
    assert settings.llm_provider == "stub"
    assert settings.model_provider_mode == "fully_pluggable"
    assert settings.output_path_mode == "relative_and_absolute"
    assert settings.electronic_structure_mode == "style_pack"
    assert settings.acoustic_accompaniment_default == "guitar_first"
    assert settings.deployment_profile == "app"


def test_settings_can_be_overridden_without_env_file(monkeypatch):
    monkeypatch.setenv("MUSICAGENT_INPUT_MODE", "reference")
    monkeypatch.setenv("MUSICAGENT_DEPLOYMENT_PROFILE", "agent")

    settings = load_settings()

    assert settings.input_mode == "reference"
    assert settings.deployment_profile == "agent"


def test_settings_public_snapshot_redacts_secret_values(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "super-secret-token")

    snapshot = load_settings().public_snapshot()

    assert "super-secret-token" not in str(snapshot)
    assert snapshot["has_openai_api_key"] is True
