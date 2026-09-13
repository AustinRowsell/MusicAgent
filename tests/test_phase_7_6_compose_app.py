from pathlib import Path

import yaml


def test_compose_app_profile_has_cli_and_web_services():
    compose = yaml.safe_load(Path("compose.yaml").read_text())
    services = compose["services"]

    assert "musicagent-cli" in services
    assert "musicagent-web" in services
    assert "app" in services["musicagent-cli"]["profiles"]
    assert "app" in services["musicagent-web"]["profiles"]


def test_compose_app_services_mount_outputs_and_inputs():
    compose = yaml.safe_load(Path("compose.yaml").read_text())

    for service_name in ("musicagent-cli", "musicagent-web"):
        volumes = compose["services"][service_name]["volumes"]
        assert "./outputs:/app/outputs" in volumes
        assert "./inputs:/app/inputs:ro" in volumes


def test_compose_web_exposes_fastapi_port_and_uses_env_file():
    compose = yaml.safe_load(Path("compose.yaml").read_text())
    web = compose["services"]["musicagent-web"]

    assert "8000:8000" in web["ports"]
    assert {"path": ".env", "required": False} in web["env_file"]
    assert web["command"] == [
        "uvicorn",
        "musicagent.web.app:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
    ]


def test_compose_does_not_inline_secret_values():
    content = Path("compose.yaml").read_text().lower()

    assert "sk-" not in content
    assert "secret-value" not in content
