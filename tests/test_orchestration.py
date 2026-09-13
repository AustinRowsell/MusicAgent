from musicagent.models import ProjectRequest
from musicagent.orchestration.crew import CrewProjectGenerator, StubAgentRunner


def test_electronic_crew_task_graph_runs_named_agents(tmp_path):
    request = ProjectRequest(
        name="Neon Test",
        prompt="indietronica with a bright drop",
        output_root=tmp_path,
        crew="electronic_alt_pop",
        dry_run=True,
    )

    result = CrewProjectGenerator(agent_runner=StubAgentRunner()).generate(request)

    assert result.crew.id == "electronic_alt_pop"
    assert result.executed_agents == (
        "groove_architect",
        "sound_designer",
        "cyber_critic",
    )
    assert (result.project.root / "groove_plan.md").exists()
    assert (result.project.root / "sound_design.md").exists()
    assert (result.project.root / "cyber_critic_review.md").exists()
    assert (result.project.root / "data" / "groove_plan.json").exists()


def test_acoustic_crew_task_graph_runs_named_agents(tmp_path):
    request = ProjectRequest(
        name="Acoustic Test",
        prompt="intimate acoustic song about distance",
        output_root=tmp_path,
        crew="singer_songwriter_acoustic",
        dry_run=True,
    )

    result = CrewProjectGenerator(agent_runner=StubAgentRunner()).generate(request)

    assert result.crew.id == "singer_songwriter_acoustic"
    assert result.executed_agents == (
        "lyricist_poet",
        "topliner",
        "harmonic_accompanist",
    )
    assert (result.project.root / "lyrics.md").exists()
    assert (result.project.root / "topline.md").exists()
    assert (result.project.root / "accompaniment.md").exists()
    assert (result.project.root / "data" / "topline.json").exists()


def test_crew_generator_resolves_style_alias(tmp_path):
    request = ProjectRequest(
        name="Alias Test",
        prompt="soft folk acoustic",
        output_root=tmp_path,
        crew="folk_acoustic",
        dry_run=True,
    )

    result = CrewProjectGenerator(agent_runner=StubAgentRunner()).generate(request)

    assert result.crew.id == "singer_songwriter_acoustic"
    assert (result.project.midi_dir / "vocal_melody.mid").exists()
    assert (result.project.midi_dir / "accompaniment.mid").exists()
    assert not (result.project.midi_dir / "full_sketch.mid").exists()
