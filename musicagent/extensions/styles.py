"""Style pack creation workflow."""

from __future__ import annotations

from pathlib import Path

from musicagent.models import StylePack
from musicagent.registries.styles import write_style_pack


class StylePackCreator:
    """Create file-backed style packs without changing core orchestration code."""

    def __init__(self, style_dir: Path) -> None:
        self._style_dir = style_dir

    def create(
        self,
        style_id: str,
        display_name: str,
        tempo_range: tuple[int, int],
        common_keys: tuple[str, ...],
        instrumentation: tuple[str, ...],
        recommended_agents: tuple[str, ...],
    ) -> StylePack:
        style = StylePack(
            id=style_id,
            display_name=display_name,
            tempo_range=tempo_range,
            common_keys=common_keys,
            instrumentation=instrumentation,
            recommended_agents=recommended_agents,
        )
        write_style_pack(self._style_dir / f"{style_id}.toml", style)
        return style
