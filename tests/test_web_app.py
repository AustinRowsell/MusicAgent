from pathlib import Path

from fastapi.testclient import TestClient
from musicagent.web.app import create_app


def test_web_home_renders_project_dashboard():
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "MusicAgent" in response.text


def test_web_api_lists_crews():
    client = TestClient(create_app())

    response = client.get("/api/crews")

    assert response.status_code == 200
    crew_ids = {crew["id"] for crew in response.json()["crews"]}
    assert "electronic_alt_pop" in crew_ids
    assert "singer_songwriter_acoustic" in crew_ids


def test_web_api_config_returns_non_secret_diagnostics(monkeypatch):
    monkeypatch.setenv("MUSICAGENT_LLM_PROVIDER", "openai-compatible")
    monkeypatch.setenv("MUSICAGENT_MODEL", "llama3.1:8b")
    monkeypatch.setenv("MUSICAGENT_OPENAI_BASE_URL", "http://user:password@ollama:11434/v1")
    monkeypatch.setenv("OPENAI_API_KEY", "super-secret-token")
    client = TestClient(create_app())

    response = client.get("/api/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "openai-compatible"
    assert payload["base_url_host"] == "ollama:11434"
    assert payload["has_openai_api_key"] is True
    assert "super-secret-token" not in response.text
    assert "password" not in response.text


def test_web_api_creates_project_and_lists_assets(tmp_path: Path):
    client = TestClient(create_app())

    create_response = client.post(
        "/api/projects",
        json={
            "name": "Web Project",
            "prompt": "web generated indietronica",
            "crew": "indietronica",
            "output_root": str(tmp_path),
            "dry_run": True,
        },
    )

    assert create_response.status_code == 200
    project_root = Path(create_response.json()["project_root"])
    assert (project_root / "midi" / "drums.mid").exists()

    assets_response = client.get(
        "/api/projects/web-project/assets",
        params={"output_root": str(tmp_path)},
    )

    assert assets_response.status_code == 200
    paths = {asset["path"] for asset in assets_response.json()["assets"]}
    assert "midi/drums.mid" in paths
    assert "sound_design.md" in paths


def test_web_api_downloads_midi_asset(tmp_path: Path):
    client = TestClient(create_app())
    client.post(
        "/api/projects",
        json={
            "name": "Download Project",
            "prompt": "download test",
            "crew": "acoustic",
            "output_root": str(tmp_path),
            "dry_run": True,
        },
    )

    response = client.get(
        "/api/projects/download-project/midi/vocal_melody.mid",
        params={"output_root": str(tmp_path)},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] in {"audio/midi", "audio/x-midi"}
    assert response.content
