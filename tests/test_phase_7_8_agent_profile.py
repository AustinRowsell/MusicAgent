from pathlib import Path

import yaml
from musicagent.cli import app
from musicagent.registries.agents import built_in_agents
from typer.testing import CliRunner

runner = CliRunner()


EXPECTED_AGENT_SERVICES = {
    "groove-architect-agent": "groove_architect",
    "sound-designer-agent": "sound_designer",
    "cyber-critic-agent": "cyber_critic",
    "lyricist-poet-agent": "lyricist_poet",
    "topliner-agent": "topliner",
    "harmonic-accompanist-agent": "harmonic_accompanist",
}


def test_compose_agents_profile_covers_all_builtin_agents():
    compose = yaml.safe_load(Path("compose.yaml").read_text())
    services = compose["services"]
    registry_agent_ids = {agent.id for agent in built_in_agents()}

    assert set(EXPECTED_AGENT_SERVICES.values()) == registry_agent_ids
    for service_name, agent_id in EXPECTED_AGENT_SERVICES.items():
        service = services[service_name]
        assert "agents" in service["profiles"]
        assert service["environment"]["MUSICAGENT_DEPLOYMENT_PROFILE"] == "agent"
        assert service["environment"]["MUSICAGENT_AGENT_ID"] == agent_id
        assert service["command"] == ["musicagent", "agent-worker", "--agent-id", agent_id]


def test_agent_worker_logs_configured_agent_id_without_secret_values():
    result = runner.invoke(app, ["agent-worker", "--agent-id", "groove_architect"])

    assert result.exit_code == 0
    assert "agent worker ready: groove_architect" in result.stdout
    assert "secret" not in result.stdout.lower()
