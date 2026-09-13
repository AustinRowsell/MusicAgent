from pathlib import Path

import yaml
from musicagent.cli import app
from typer.testing import CliRunner

runner = CliRunner()


EXPECTED_CREW_SERVICES = {
    "electronic-alt-pop-crew": "electronic_alt_pop",
    "singer-songwriter-acoustic-crew": "singer_songwriter_acoustic",
}


def test_compose_crews_profile_contains_each_builtin_crew_service():
    compose = yaml.safe_load(Path("compose.yaml").read_text())
    services = compose["services"]

    for service_name, crew_id in EXPECTED_CREW_SERVICES.items():
        service = services[service_name]
        assert "crews" in service["profiles"]
        assert service["environment"]["MUSICAGENT_DEPLOYMENT_PROFILE"] == "crew"
        assert service["environment"]["MUSICAGENT_CREW_ID"] == crew_id
        assert service["command"] == ["musicagent", "crew-worker", "--crew-id", crew_id]


def test_crew_worker_logs_configured_crew_id_without_secret_values():
    result = runner.invoke(app, ["crew-worker", "--crew-id", "electronic_alt_pop"])

    assert result.exit_code == 0
    assert "crew worker ready: electronic_alt_pop" in result.stdout
    assert "secret" not in result.stdout.lower()


def test_each_crew_smoke_command_generates_crew_specific_outputs(tmp_path):
    electronic = runner.invoke(
        app,
        [
            "create",
            "--name",
            "electronic-smoke",
            "--prompt",
            "electronic container smoke",
            "--crew",
            "electronic_alt_pop",
            "--output",
            str(tmp_path),
            "--dry-run",
        ],
    )
    acoustic = runner.invoke(
        app,
        [
            "create",
            "--name",
            "acoustic-smoke",
            "--prompt",
            "acoustic container smoke",
            "--crew",
            "singer_songwriter_acoustic",
            "--output",
            str(tmp_path),
            "--dry-run",
        ],
    )

    assert electronic.exit_code == 0
    assert acoustic.exit_code == 0
    assert (tmp_path / "electronic-smoke" / "midi" / "drums.mid").exists()
    assert (tmp_path / "electronic-smoke" / "midi" / "bass.mid").exists()
    assert (tmp_path / "acoustic-smoke" / "midi" / "vocal_melody.mid").exists()
    assert (tmp_path / "acoustic-smoke" / "midi" / "accompaniment.mid").exists()
