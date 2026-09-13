from pathlib import Path

from musicagent.io.inputs import InputMaterialReader
from musicagent.models import InputMaterialType


def test_reader_creates_text_prompt_material():
    material = InputMaterialReader().from_prompt("A warm indietronica chorus")

    assert material.id == "main_prompt"
    assert material.type is InputMaterialType.TEXT_PROMPT
    assert material.content == "A warm indietronica chorus"
    assert material.priority == "high"


def test_reader_detects_markdown_file(tmp_path: Path):
    source = tmp_path / "brief.md"
    markdown = """# Reference
Keep it intimate."""
    source.write_text(markdown)

    material = InputMaterialReader().from_path(source)

    assert material.type is InputMaterialType.MARKDOWN
    assert material.path == source
    assert material.content == markdown
