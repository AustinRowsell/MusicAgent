from pathlib import Path

INSTALLER = Path("scripts/install.sh")


def test_installer_script_exists_and_is_executable():
    assert INSTALLER.exists()
    assert INSTALLER.stat().st_mode & 0o111


def test_installer_bootstraps_local_cli_without_global_mutation_by_default():
    content = INSTALLER.read_text()

    assert "uv sync" in content
    assert "chmod +x scripts/*.sh" in content
    assert "uv run musicagent crews" in content
    assert "uv tool install" in content
    assert "INSTALL_MODE" in content


def test_installer_guards_against_split_brain_virtualenvs():
    content = INSTALLER.read_text()

    assert 'PYTHON_REQUIREMENT=">=3.14,<3.15"' in content
    assert "ensure_consistent_venv" in content
    assert 'importlib.util.find_spec("pip")' in content
    assert "site-packages matches interpreter" in content
    assert 'uv venv --seed --python "$PYTHON_REQUIREMENT" .venv' in content
    assert 'uv sync --dev --python "$PYTHON_REQUIREMENT"' in content
    assert "rm -rf .venv" in content


def test_installer_has_no_secret_like_literals():
    content = INSTALLER.read_text().lower()

    assert "secret-value" not in content
    assert "sk-" not in content
    assert "bearer " not in content
