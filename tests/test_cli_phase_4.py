from pathlib import Path

from musicagent.cli import app
from musicagent.midi.analysis import PrettyMidiAnalyzer
from typer.testing import CliRunner


def test_cli_accepts_multiple_input_materials_and_alias_crew(tmp_path: Path):
    notes = tmp_path / "notes.md"
    notes.write_text("""# Notes
Sparse verses, bigger chorus.""")

    result = CliRunner().invoke(
        app,
        [
            "create",
            "--name",
            "Alias Inputs",
            "--prompt",
            "acoustic song",
            "--crew",
            "acoustic",
            "--input",
            str(notes),
            "--output",
            str(tmp_path),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    project_root = tmp_path / "alias-inputs"
    assert (project_root / "inputs" / "notes.md").exists()
    assert (project_root / "lyrics.md").exists()
    assert (project_root / "topline.md").exists()
    assert (project_root / "midi" / "vocal_melody.mid").exists()
    assert PrettyMidiAnalyzer().summarise(project_root / "midi" / "vocal_melody.mid").note_count > 0


def test_cli_non_dry_run_uses_stub_runner_until_live_llm_is_configured(tmp_path: Path):
    result = CliRunner().invoke(
        app,
        [
            "create",
            "--name",
            "Non Dry Run",
            "--prompt",
            "electro pop test",
            "--crew",
            "electro_pop",
            "--output",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    project_root = tmp_path / "non-dry-run"
    assert (project_root / "sound_design.md").exists()
    assert (project_root / "cyber_critic_review.md").exists()
    assert (project_root / "midi" / "drums.mid").exists()
    assert not (project_root / "midi" / "full_sketch.mid").exists()
