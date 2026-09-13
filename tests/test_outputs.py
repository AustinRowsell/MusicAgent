from pathlib import Path

import pytest
from musicagent.io.outputs import LocalOutputStore
from musicagent.models import GeneratedAsset, ProjectRequest


def test_output_store_creates_expected_project_tree(tmp_path: Path):
    request = ProjectRequest(name="Demo Song", prompt="warm synth pop", output_root=tmp_path)

    project = LocalOutputStore().create_project(request)

    assert project.root == tmp_path / "demo-song"
    assert project.midi_dir.is_dir()
    assert project.data_dir.is_dir()
    assert project.inputs_dir.is_dir()


def test_output_store_refuses_to_overwrite_existing_project(tmp_path: Path):
    request = ProjectRequest(name="Demo Song", prompt="warm synth pop", output_root=tmp_path)
    store = LocalOutputStore()
    store.create_project(request)

    with pytest.raises(FileExistsError):
        store.create_project(request)


def test_manifest_records_generated_assets(tmp_path: Path):
    request = ProjectRequest(name="Demo Song", prompt="warm synth pop", output_root=tmp_path)
    project = LocalOutputStore().create_project(request)
    asset = GeneratedAsset(kind="midi", path=project.midi_dir / "bass.mid", description="Bass MIDI")

    manifest_path = LocalOutputStore().write_manifest(project, request, [asset])

    assert manifest_path.exists()
    manifest = manifest_path.read_text()
    assert "bass.mid" in manifest
    assert "warm synth pop" in manifest
