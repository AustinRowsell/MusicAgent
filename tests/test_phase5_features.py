from pathlib import Path

from musicagent.extensions.lyricists import LyricistPersonaCreator
from musicagent.extensions.regeneration import RegenerationService
from musicagent.extensions.styles import StylePackCreator
from musicagent.extensions.templates import BatchProjectRunner, ProjectTemplateStore
from musicagent.models import ProjectRequest
from musicagent.orchestration.crew import CrewProjectGenerator, StubAgentRunner
from musicagent.registries.lyricists import FileLyricistRegistry
from musicagent.registries.styles import FileStyleRegistry


def test_style_pack_creation_workflow_adds_new_style(tmp_path: Path):
    creator = StylePackCreator(tmp_path)

    style = creator.create(
        style_id="dream_pop",
        display_name="Dream Pop",
        tempo_range=(80, 115),
        common_keys=("C major", "A minor"),
        instrumentation=("drums", "bass", "chords", "lead"),
        recommended_agents=("groove_architect", "sound_designer"),
    )

    loaded = FileStyleRegistry(tmp_path).get("dream_pop")
    assert style == loaded
    assert (tmp_path / "dream_pop.toml").exists()


def test_lyricist_persona_creation_workflow_adds_new_persona(tmp_path: Path):
    creator = LyricistPersonaCreator(tmp_path)

    persona = creator.create(
        persona_id="rap_storyteller",
        display_name="Rap Storyteller",
        role="Narrative rap lyricist",
        responsibilities=("internal rhyme", "scene detail", "cadence"),
    )

    loaded = FileLyricistRegistry(tmp_path).get("rap_storyteller")
    assert persona == loaded
    assert (tmp_path / "rap_storyteller.json").exists()


def test_regeneration_replaces_only_requested_midi_part(tmp_path: Path):
    request = ProjectRequest(
        name="Regenerate Test",
        prompt="electro pop",
        output_root=tmp_path,
        crew="electronic_alt_pop",
        dry_run=True,
    )
    result = CrewProjectGenerator(agent_runner=StubAgentRunner()).generate(request)
    bass_path = result.project.midi_dir / "bass.mid"
    drums_path = result.project.midi_dir / "drums.mid"
    original_bass_bytes = bass_path.read_bytes()
    original_drums_bytes = drums_path.read_bytes()

    RegenerationService().regenerate_part(result.project, "bass", tempo_bpm=90)

    assert bass_path.read_bytes() != original_bass_bytes
    assert drums_path.read_bytes() == original_drums_bytes
    assert not (result.project.midi_dir / "full_sketch.mid").exists()


def test_project_template_and_batch_manifest_workflow(tmp_path: Path):
    template_store = ProjectTemplateStore(tmp_path / "templates")
    template = template_store.create_template(
        template_id="quick_acoustic",
        crew="singer_songwriter_acoustic",
        tempo_bpm=82,
        key="G major",
    )
    manifest = tmp_path / "batch.json"
    manifest.write_text(
        '{"projects":[{"name":"Batch One","prompt":"first song","template":"quick_acoustic"},'
        '{"name":"Batch Two","prompt":"second song","crew":"electronic_alt_pop"}]}'
    )

    results = BatchProjectRunner(template_store=template_store).run_manifest(
        manifest, tmp_path / "outputs"
    )

    assert template.id == "quick_acoustic"
    assert len(results) == 2
    assert (tmp_path / "outputs" / "batch-one" / "midi" / "vocal_melody.mid").exists()
    assert (tmp_path / "outputs" / "batch-two" / "midi" / "drums.mid").exists()


def test_refinement_pass_writes_review_outputs(tmp_path: Path):
    request = ProjectRequest(
        name="Refine Test",
        prompt="tight indietronica arrangement",
        output_root=tmp_path,
        crew="electronic_alt_pop",
        dry_run=True,
        review_pass=True,
    )

    result = CrewProjectGenerator(agent_runner=StubAgentRunner()).generate(request)

    assert "reviewer" in result.executed_agents
    assert (result.project.root / "review.md").exists()
    assert (result.project.root / "data" / "review.json").exists()
