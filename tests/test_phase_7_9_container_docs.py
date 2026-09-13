from pathlib import Path


def test_containerisation_documentation_covers_operator_workflows():
    content = Path("docs/planning/containerisation-decisions.md").read_text()

    required_sections = [
        "## Local CLI run",
        "## Local web run",
        "## Compose app profile",
        "## Compose crew profile",
        "## Compose agent profile",
        "## Output mounts",
        "## Environment configuration",
        "## Troubleshooting",
    ]
    for section in required_sections:
        assert section in content


def test_containerisation_documentation_has_required_examples_and_no_fake_secrets():
    content = Path("docs/planning/containerisation-decisions.md").read_text()

    required_examples = [
        "docker compose --profile app run --rm musicagent-cli crews",
        "docker compose --profile crews run --rm electronic-alt-pop-crew",
        "docker compose --profile agents run --rm groove-architect-agent",
        "uv run musicagent create --name electronic-example",
        "uv run musicagent create --name acoustic-example",
        "curl http://localhost:8000/api/crews",
        "midi/drums.mid",
        "midi/vocal_melody.mid",
    ]
    for example in required_examples:
        assert example in content

    assert "sk-" not in content.lower()
    assert "secret-value" not in content.lower()
    assert "deployment profiles, not separate code forks" in content
