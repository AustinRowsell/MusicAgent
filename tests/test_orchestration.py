from dataclasses import dataclass, field
from types import SimpleNamespace

from musicagent.models import ProjectRequest
from musicagent.orchestration.crew import CrewProjectGenerator, LLMAgentRunner, StubAgentRunner
from musicagent.orchestration.llm import AgentModelRouter


@dataclass
class RecordingLLMClient:
    required_environment_variables: tuple[str, ...] = ()
    calls: list[tuple[str, str | None]] = field(default_factory=list)

    def complete(self, agent_id: str, prompt: str, model: str | None = None) -> str:
        self.calls.append((agent_id, model))
        return (
            '{"agent_id":"'
            + agent_id
            + '","summary":"'
            + agent_id
            + " via "
            + str(model)
            + '","sections":["section"],"actions":["action"],"confidence":0.8}'
        )


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


def test_crew_generator_default_stub_runner_writes_valid_structured_output(tmp_path, monkeypatch):
    monkeypatch.delenv("MUSICAGENT_LLM_PROVIDER", raising=False)
    request = ProjectRequest(
        name="Default Stub Structured",
        prompt="verify default stub structure",
        output_root=tmp_path,
        crew="acoustic",
        dry_run=True,
    )

    result = CrewProjectGenerator().generate(request)

    lyrics_payload = (result.project.root / "data" / "lyrics.json").read_text()
    assert '"structured_output_valid": true' in lyrics_payload
    assert (
        '"summary": "Stub response for lyricist_poet: verify default stub structure"'
        in lyrics_payload
    )


def test_llm_agent_runner_routes_models_per_agent():
    client = RecordingLLMClient()
    runner = LLMAgentRunner(
        llm_client=client,
        model_router=AgentModelRouter(
            default_model="llama3.1:8b",
            agent_model_overrides={"lyricist_poet": "mistral-nemo:12b"},
        ),
    )

    lyric_output = runner.run("lyricist_poet", "write a chorus")
    groove_output = runner.run("groove_architect", "write a beat")

    assert lyric_output.valid is True
    assert lyric_output.output.summary == "lyricist_poet via mistral-nemo:12b"
    assert groove_output.valid is True
    assert groove_output.output.summary == "groove_architect via llama3.1:8b"
    assert client.calls == [
        ("lyricist_poet", "mistral-nemo:12b"),
        ("groove_architect", "llama3.1:8b"),
    ]


def test_crew_generator_default_runner_uses_configured_local_llm_models(tmp_path, monkeypatch):
    monkeypatch.setenv("MUSICAGENT_LLM_PROVIDER", "openai-compatible")
    monkeypatch.setenv("MUSICAGENT_MODEL", "llama3.1:8b")
    monkeypatch.setenv("MUSICAGENT_OPENAI_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "ollama-local-placeholder")
    monkeypatch.setenv("MUSICAGENT_USE_LOW_RESOURCE_MODEL", "false")
    monkeypatch.setenv("MUSICAGENT_AGENT_MODEL_LYRICIST_POET", "mistral-nemo:12b")
    monkeypatch.setenv("MUSICAGENT_AGENT_MODEL_TOPLINER", "mistral-nemo:12b")

    calls: list[tuple[str, str | None, str | None]] = []

    class FakeOpenAI:
        def __init__(self, base_url: str | None = None) -> None:
            self.base_url = base_url
            self.chat = self
            self.completions = self

        def create(self, model: str, messages: list[dict[str, str]]) -> object:
            prompt = messages[0]["content"]
            calls.append(("init", model, self.base_url))
            calls.append(("invoke", model, prompt.splitlines()[0]))

            content = (
                '{"agent_id":"'
                + prompt.splitlines()[0].removeprefix("Agent: ")
                + '","summary":"fake local llm response",'
                + '"sections":["verse"],"actions":["revise hook"],"confidence":0.7}'
            )
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)
    request = ProjectRequest(
        name="Model Routing",
        prompt="write an intimate chorus",
        output_root=tmp_path,
        crew="singer_songwriter_acoustic",
        dry_run=True,
    )

    result = CrewProjectGenerator().generate(request)

    assert result.executed_agents == ("lyricist_poet", "topliner", "harmonic_accompanist")
    init_calls = [call for call in calls if call[0] == "init"]
    assert init_calls == [
        ("init", "mistral-nemo:12b", "http://ollama:11434/v1"),
        ("init", "mistral-nemo:12b", "http://ollama:11434/v1"),
        ("init", "llama3.1:8b", "http://ollama:11434/v1"),
    ]


def test_crew_generator_low_resource_mode_overrides_agent_models(tmp_path, monkeypatch):
    monkeypatch.setenv("MUSICAGENT_LLM_PROVIDER", "openai-compatible")
    monkeypatch.setenv("MUSICAGENT_MODEL", "llama3.1:8b")
    monkeypatch.setenv("MUSICAGENT_OPENAI_BASE_URL", "http://ollama:11434/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "ollama-local-placeholder")
    monkeypatch.setenv("MUSICAGENT_AGENT_MODEL_LYRICIST_POET", "mistral-nemo:12b")
    monkeypatch.setenv("MUSICAGENT_LOW_RESOURCE_MODEL", "llama3.2:3b")
    monkeypatch.setenv("MUSICAGENT_USE_LOW_RESOURCE_MODEL", "true")

    models: list[str] = []

    class FakeOpenAI:
        def __init__(self, base_url: str | None = None) -> None:
            self.chat = self
            self.completions = self

        def create(self, model: str, messages: list[dict[str, str]]) -> object:
            prompt = messages[0]["content"]
            models.append(model)

            content = (
                '{"agent_id":"'
                + prompt.splitlines()[0].removeprefix("Agent: ")
                + '","summary":"fake low-resource response",'
                + '"sections":[],"actions":[],"confidence":0.6}'
            )
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)
    request = ProjectRequest(
        name="Low Resource Routing",
        prompt="write a tiny acoustic sketch",
        output_root=tmp_path,
        crew="singer_songwriter_acoustic",
        dry_run=True,
    )

    CrewProjectGenerator().generate(request)

    assert models == ["llama3.2:3b", "llama3.2:3b", "llama3.2:3b"]
