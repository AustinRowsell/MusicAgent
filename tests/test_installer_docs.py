from pathlib import Path


def test_operator_docs_reference_installer_script():
    content = Path("docs/planning/containerisation-decisions.md").read_text()

    assert "./scripts/install.sh" in content
    assert "./scripts/install.sh --user" in content
    assert "uv run musicagent crews" in content
