from pathlib import Path

EXPECTED_SCRIPTS = {
    "scripts/local-cli.sh",
    "scripts/local-web.sh",
    "scripts/docker-common.sh",
    "scripts/docker-cli.sh",
    "scripts/docker-create.sh",
    "scripts/docker-web.sh",
    "scripts/docker-crew.sh",
    "scripts/docker-agent.sh",
    "scripts/docker-local-llm-pull.sh",
    "scripts/docker-local-llm-web.sh",
    "scripts/docker-local-llm-create.sh",
    "scripts/docker-local-llm-check.sh",
}


def test_helper_scripts_exist_and_are_executable():
    for script_path in EXPECTED_SCRIPTS:
        path = Path(script_path)
        assert path.exists()
        assert path.stat().st_mode & 0o111


def test_docker_helper_scripts_hide_compose_profile_details():
    docker_common = Path("scripts/docker-common.sh").read_text()
    docker_cli = Path("scripts/docker-cli.sh").read_text()
    docker_create = Path("scripts/docker-create.sh").read_text()
    docker_web = Path("scripts/docker-web.sh").read_text()
    docker_crew = Path("scripts/docker-crew.sh").read_text()
    docker_agent = Path("scripts/docker-agent.sh").read_text()
    docker_local_llm_pull = Path("scripts/docker-local-llm-pull.sh").read_text()
    docker_local_llm_create = Path("scripts/docker-local-llm-create.sh").read_text()
    docker_local_llm_web = Path("scripts/docker-local-llm-web.sh").read_text()
    docker_local_llm_check = Path("scripts/docker-local-llm-check.sh").read_text()

    assert "find certs -maxdepth 1" in docker_common
    assert "musicagent-local-ca-bundle.pem" in docker_common
    assert "compose.local-certs.yaml" in docker_common

    for script in (
        docker_cli,
        docker_create,
        docker_web,
        docker_crew,
        docker_agent,
        docker_local_llm_pull,
        docker_local_llm_create,
        docker_local_llm_web,
        docker_local_llm_check,
    ):
        assert "source \"${SCRIPT_DIR}/docker-common.sh\"" in script
        assert "use_optional_local_ca_compose_override" in script

    assert "docker compose --profile app run --rm musicagent-cli musicagent" in docker_cli
    assert "docker compose --profile app run --rm musicagent-cli musicagent create" in docker_create
    assert "docker compose --profile app up musicagent-web" in docker_web
    assert "docker compose --profile crews run --rm" in docker_crew
    assert "docker compose --profile agents run --rm" in docker_agent
    assert "Using optional local CA certificates from ./certs" in docker_local_llm_pull
    assert "docker compose --profile local-llm up -d ollama" in docker_local_llm_pull
    assert "docker compose --profile local-llm exec ollama ollama pull" in docker_local_llm_pull
    assert (
        "docker compose --profile local-llm run --rm musicagent-local-llm-cli musicagent create"
        in docker_local_llm_create
    )
    assert "docker compose --profile local-llm up musicagent-local-llm-web" in docker_local_llm_web
    assert (
        "docker compose --profile local-llm run --rm musicagent-local-llm-cli musicagent llm-check"
        in docker_local_llm_check
    )


def test_helper_scripts_do_not_contain_secret_like_literals():
    for script_path in EXPECTED_SCRIPTS:
        content = Path(script_path).read_text().lower()
        assert "secret-value" not in content
        assert "sk-" not in content
        assert "bearer " not in content
