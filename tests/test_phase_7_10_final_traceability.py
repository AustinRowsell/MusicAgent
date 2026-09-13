from pathlib import Path

import yaml
from musicagent.cli import app
from musicagent.config import MusicAgentSettings
from typer.testing import CliRunner

runner = CliRunner()


def test_phase_7_decisions_are_represented_in_config_and_container_files():
    settings = MusicAgentSettings()
    snapshot = settings.public_snapshot()
    compose = yaml.safe_load(Path("compose.yaml").read_text())
    dockerignore = Path(".dockerignore").read_text().splitlines()
    gitignore = Path(".gitignore").read_text().splitlines()
    docs = Path("docs/planning/containerisation-decisions.md").read_text()

    assert snapshot["interface_mode"] == "both"
    assert snapshot["midi_metadata_mode"] == "names_and_general_midi"
    assert snapshot["input_mode"] == "copy"
    assert snapshot["audio_mode"] == "metadata_only"
    assert snapshot["model_provider_mode"] == "fully_pluggable"
    assert snapshot["output_path_mode"] == "relative_and_absolute"
    assert snapshot["electronic_structure_mode"] == "style_pack"
    assert snapshot["acoustic_accompaniment_default"] == "guitar_first"
    assert {"app", "crews", "agents"}.issubset(
        {profile for service in compose["services"].values() for profile in service["profiles"]}
    )
    assert "Dockerfile" in {path.name for path in Path(".").iterdir()}
    assert "compose.yaml" in {path.name for path in Path(".").iterdir()}
    assert ".env" in dockerignore
    assert "outputs/" in dockerignore
    assert ".env" in gitignore
    assert "!.env.example" in gitignore
    assert "./outputs:/app/outputs" in docs


def test_phase_7_final_smoke_keeps_cli_and_web_on_shared_generation_outputs(tmp_path, monkeypatch):
    monkeypatch.delenv("MUSICAGENT_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("MUSICAGENT_MODEL", raising=False)
    monkeypatch.delenv("MUSICAGENT_OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = runner.invoke(
        app,
        [
            "create",
            "--name",
            "phase-7-10-smoke",
            "--prompt",
            "final decision traceability smoke",
            "--crew",
            "electronic_alt_pop",
            "--output",
            str(tmp_path),
            "--dry-run",
        ],
    )

    project_root = tmp_path / "phase-7-10-smoke"
    assert result.exit_code == 0
    assert (project_root / "session_manifest.json").exists()
    assert (project_root / "midi" / "drums.mid").exists()
    assert (project_root / "midi" / "bass.mid").exists()
    assert not (project_root / "midi" / "full_sketch.mid").exists()


def test_phase_7_files_do_not_contain_known_secret_like_literals():
    checked_files = [
        Path("compose.yaml"),
        Path(".env.example"),
        Path("docs/planning/containerisation-decisions.md"),
    ]

    for path in checked_files:
        content = path.read_text().lower()
        assert "secret-value" not in content
        assert "sk-" not in content
        assert "bearer " not in content
