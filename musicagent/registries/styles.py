"""Style pack registries."""

from __future__ import annotations

import tomllib
from pathlib import Path

from musicagent.models import StylePack


class BuiltInStyleRegistry:
    """Registry for built-in style packs."""

    def __init__(self, styles: tuple[StylePack, ...]) -> None:
        self._styles = {style.id: style for style in styles}

    @classmethod
    def default(cls) -> BuiltInStyleRegistry:
        electronic_radio = StylePack(
            id="electronic_radio_pop",
            display_name="Electronic Radio Pop",
            tempo_range=(95, 125),
            common_keys=("A minor", "C major", "D minor"),
            instrumentation=("drums", "bass", "chords", "hooks"),
            recommended_agents=("groove_architect", "sound_designer", "cyber_critic"),
            structure_profile="radio_pop",
            structure=("intro", "verse", "pre_chorus", "chorus", "bridge", "chorus", "outro"),
        )
        electronic_club = StylePack(
            id="electronic_club_extended",
            display_name="Electronic Club Extended",
            tempo_range=(118, 132),
            common_keys=("A minor", "C minor", "D minor"),
            instrumentation=("drums", "bass", "chords", "hooks"),
            recommended_agents=("groove_architect", "sound_designer", "cyber_critic"),
            structure_profile="club_extended",
            structure=("intro", "build", "drop", "breakdown", "build", "drop", "outro"),
        )
        return cls(
            styles=(
                StylePack(
                    id="electronic_alt_pop",
                    display_name="Electronic Alt Pop",
                    tempo_range=(95, 130),
                    common_keys=("A minor", "C major", "D minor"),
                    instrumentation=("drums", "bass", "chords", "hooks"),
                    recommended_agents=("groove_architect", "sound_designer", "cyber_critic"),
                    structure_profile="style_pack",
                    structure=electronic_radio.structure,
                ),
                electronic_radio,
                electronic_club,
                StylePack(
                    id="singer_songwriter_acoustic",
                    display_name="Singer-Songwriter Acoustic",
                    tempo_range=(65, 110),
                    common_keys=("C major", "G major", "A minor"),
                    instrumentation=("vocal_melody", "accompaniment"),
                    recommended_agents=("lyricist_poet", "topliner", "harmonic_accompanist"),
                    structure_profile="guitar_first_acoustic",
                    structure=("intro", "verse", "chorus", "verse", "chorus", "bridge", "chorus"),
                    accompaniment_default="guitar_first",
                ),
            )
        )

    def get(self, style_id: str) -> StylePack:
        try:
            return self._styles[style_id]
        except KeyError as error:
            raise KeyError(f"Unknown style pack: {style_id}") from error


class FileStyleRegistry:
    """Registry for user-created style packs stored as TOML files."""

    def __init__(self, style_dir: Path) -> None:
        self._style_dir = style_dir

    def get(self, style_id: str) -> StylePack:
        path = self._style_dir / f"{style_id}.toml"
        if not path.exists():
            raise KeyError(f"Unknown style pack: {style_id}")
        data = tomllib.loads(path.read_text())
        return StylePack(
            id=data["id"],
            display_name=data["display_name"],
            tempo_range=(data["tempo_min"], data["tempo_max"]),
            common_keys=tuple(data["common_keys"]),
            instrumentation=tuple(data["instrumentation"]),
            recommended_agents=tuple(data["recommended_agents"]),
            structure_profile=data.get("structure_profile", "default"),
            structure=tuple(data.get("structure", [])),
            accompaniment_default=data.get("accompaniment_default"),
        )


def write_style_pack(path: Path, style: StylePack) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f'id = "{style.id}"',
        f'display_name = "{style.display_name}"',
        f"tempo_min = {style.tempo_range[0]}",
        f"tempo_max = {style.tempo_range[1]}",
        f'structure_profile = "{style.structure_profile}"',
        _toml_array("common_keys", style.common_keys),
        _toml_array("instrumentation", style.instrumentation),
        _toml_array("recommended_agents", style.recommended_agents),
        _toml_array("structure", style.structure),
    ]
    if style.accompaniment_default is not None:
        lines.append(f'accompaniment_default = "{style.accompaniment_default}"')
    lines.append("")
    path.write_text(chr(10).join(lines))


def _toml_array(name: str, values: tuple[str, ...]) -> str:
    quoted = ", ".join(_toml_quote(value) for value in values)
    return f"{name} = [{quoted}]"


def _toml_quote(value: str) -> str:
    return '"' + value.replace('"', '"') + '"'
