from musicagent.cli import app
from typer.testing import CliRunner


def test_cli_lists_built_in_crews():
    result = CliRunner().invoke(app, ["crews"])

    assert result.exit_code == 0
    assert "electronic_alt_pop" in result.output
    assert "singer_songwriter_acoustic" in result.output


def test_cli_dry_run_creates_project_outputs(tmp_path):
    result = CliRunner().invoke(
        app,
        [
            "create",
            "--name",
            "Demo Song",
            "--prompt",
            "warm synth pop",
            "--crew",
            "electronic_alt_pop",
            "--output",
            str(tmp_path),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert (tmp_path / "demo-song" / "session_manifest.json").exists()
    assert (tmp_path / "demo-song" / "midi" / "drums.mid").exists()
    assert not (tmp_path / "demo-song" / "midi" / "full_sketch.mid").exists()
