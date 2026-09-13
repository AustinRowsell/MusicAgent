from pathlib import Path


def test_readme_documents_optional_local_ca_workflow():
    content = Path("README.md").read_text()

    assert "compose.local-certs.yaml" in content
    assert "./certs" in content
    assert "systems that do not need local certificates" in content
    assert "Git and Docker build contexts" in content


def test_singer_songwriter_e2e_documents_optional_local_ca_workflow():
    content = Path("docs/singer-songwriter-acoustic-e2e.md").read_text()

    assert "PyPI" in content
    assert "uv pip install --system --system-certs ." in content
    assert "registry.ollama.ai" in content
    assert "compose.local-certs.yaml" in content
    assert "BuildKit secret" in content
    assert "musicagent-local-ca-bundle.pem" in content
    assert "./certs" in content
    assert "If `./certs` is absent or contains no certificate files" in content
    assert "Do not commit local certificate files" in content


def test_planning_docs_document_optional_local_ca_workflow():
    docs = [
        Path("docs/planning/local-llm-support-plan.md"),
        Path("docs/planning/containerisation-decisions.md"),
    ]

    for path in docs:
        content = path.read_text()
        assert "compose.local-certs.yaml" in content
        assert "./certs" in content
        assert "ignored by Git" in content
        assert "Docker build contexts" in content


def test_containerisation_plan_keeps_certs_out_of_image_context():
    content = Path("docs/planning/phase-7-decision-gated-containerisation-plan.md").read_text()

    assert "`certs/`" in content
    assert "Image context must exclude" in content
