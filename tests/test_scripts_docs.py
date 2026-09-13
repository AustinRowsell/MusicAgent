from pathlib import Path


def test_operator_docs_reference_helper_scripts():
    content = Path("docs/planning/containerisation-decisions.md").read_text()

    for command in (
        "./scripts/local-cli.sh crews",
        "./scripts/local-web.sh",
        "./scripts/docker-cli.sh crews",
        "./scripts/docker-create.sh --name electronic-example",
        "./scripts/docker-web.sh",
        "./scripts/docker-crew.sh electronic",
        "./scripts/docker-agent.sh groove",
    ):
        assert command in content
