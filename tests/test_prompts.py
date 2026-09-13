from pathlib import Path

REQUIRED_PROMPTS = {
    "groove_architect.md",
    "sound_designer.md",
    "cyber_critic.md",
    "lyricist_poet.md",
    "topliner.md",
    "harmonic_accompanist.md",
}


def test_required_phase_3_prompt_files_exist():
    prompt_dir = Path("musicagent/prompts")

    missing = [name for name in REQUIRED_PROMPTS if not (prompt_dir / name).exists()]

    assert missing == []


def test_prompt_files_define_role_and_output_contract():
    for prompt_name in REQUIRED_PROMPTS:
        content = (Path("musicagent/prompts") / prompt_name).read_text()
        assert "Role:" in content
        assert "Output contract:" in content
