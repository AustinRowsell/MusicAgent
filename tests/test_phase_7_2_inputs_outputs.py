import json
from pathlib import Path

from musicagent.cli import app
from musicagent.io.inputs import InputMaterialReader
from musicagent.models import InputHandlingMode, InputMaterialType, ProjectRequest
from musicagent.orchestration.crew import CrewProjectGenerator
from typer.testing import CliRunner


def test_reference_input_mode_records_but_does_not_copy_input(tmp_path: Path):
    source = tmp_path / "reference.md"
    source.write_text("reference notes")
    material = InputMaterialReader().from_path(source)
    request = ProjectRequest(
        name="Reference Mode",
        prompt="use referenced notes",
        output_root=tmp_path / "out",
        crew="electronic_alt_pop",
        inputs=(material,),
        input_mode=InputHandlingMode.REFERENCE,
        dry_run=True,
    )

    result = CrewProjectGenerator().generate(request)
    manifest = json.loads((result.project.root / "session_manifest.json").read_text())

    assert not (result.project.inputs_dir / "reference.md").exists()
    assert manifest["inputs"][0]["mode"] == "reference"
    assert manifest["inputs"][0]["original_path"].endswith("reference.md")
    assert "project_path" not in manifest["inputs"][0]


def test_copy_input_mode_copies_input_and_records_manifest_metadata(tmp_path: Path):
    source = tmp_path / "reference.md"
    source.write_text("reference notes")
    material = InputMaterialReader().from_path(source)
    request = ProjectRequest(
        name="Copy Mode",
        prompt="copy notes",
        output_root=tmp_path / "out",
        crew="electronic_alt_pop",
        inputs=(material,),
        input_mode=InputHandlingMode.COPY,
        dry_run=True,
    )

    result = CrewProjectGenerator().generate(request)
    manifest = json.loads((result.project.root / "session_manifest.json").read_text())

    assert (result.project.inputs_dir / "reference.md").exists()
    assert manifest["inputs"][0]["mode"] == "copy"
    assert manifest["inputs"][0]["project_path"] == "inputs/reference.md"


def test_cli_reference_input_mode_is_user_accessible(tmp_path: Path):
    source = tmp_path / "reference.md"
    source.write_text("reference notes")

    result = CliRunner().invoke(
        app,
        [
            "create",
            "--name",
            "Cli Reference",
            "--prompt",
            "reference input",
            "--input",
            str(source),
            "--input-mode",
            "reference",
            "--output",
            str(tmp_path / "out"),
            "--dry-run",
        ],
    )

    project_root = tmp_path / "out" / "cli-reference"
    manifest = json.loads((project_root / "session_manifest.json").read_text())
    assert result.exit_code == 0
    assert not (project_root / "inputs" / "reference.md").exists()
    assert manifest["inputs"][0]["mode"] == "reference"


def test_audio_file_is_metadata_only_input(tmp_path: Path):
    source = tmp_path / "loop.wav"
    source.write_bytes(b"RIFFmetadata-only")

    material = InputMaterialReader().from_path(source)

    assert material.type is InputMaterialType.AUDIO
    assert material.content is None
    assert "metadata_only" in material.constraints


def test_manifest_records_resolved_output_root_for_relative_and_absolute_paths(tmp_path: Path):
    relative_request = ProjectRequest(
        name="Relative Output",
        prompt="relative",
        output_root=Path("outputs/test-relative-root"),
        crew="electronic_alt_pop",
        dry_run=True,
        overwrite=True,
    )
    absolute_request = ProjectRequest(
        name="Absolute Output",
        prompt="absolute",
        output_root=tmp_path / "absolute-root",
        crew="singer_songwriter_acoustic",
        dry_run=True,
    )

    relative_result = CrewProjectGenerator().generate(relative_request)
    absolute_result = CrewProjectGenerator().generate(absolute_request)
    relative_manifest = json.loads(
        (relative_result.project.root / "session_manifest.json").read_text()
    )
    absolute_manifest = json.loads(
        (absolute_result.project.root / "session_manifest.json").read_text()
    )

    assert Path(relative_manifest["resolved_output_root"]).is_absolute()
    assert Path(absolute_manifest["resolved_output_root"]).is_absolute()
    assert all(not asset["path"].startswith("/") for asset in relative_manifest["assets"])
