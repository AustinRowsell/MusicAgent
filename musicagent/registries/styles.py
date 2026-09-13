"""Built-in style pack registry."""

from __future__ import annotations

from musicagent.models import StylePack


class BuiltInStyleRegistry:
    """Registry for built-in style packs."""

    def __init__(self, styles: tuple[StylePack, ...]) -> None:
        self._styles = {style.id: style for style in styles}

    @classmethod
    def default(cls) -> BuiltInStyleRegistry:
        return cls(
            styles=(
                StylePack(
                    id="electronic_alt_pop",
                    display_name="Electronic Alt Pop",
                    tempo_range=(95, 130),
                    common_keys=("A minor", "C major", "D minor"),
                    instrumentation=("drums", "bass", "chords", "hooks"),
                    recommended_agents=("groove_architect", "sound_designer", "cyber_critic"),
                ),
                StylePack(
                    id="singer_songwriter_acoustic",
                    display_name="Singer-Songwriter Acoustic",
                    tempo_range=(65, 110),
                    common_keys=("C major", "G major", "A minor"),
                    instrumentation=("vocal_melody", "accompaniment"),
                    recommended_agents=("lyricist_poet", "topliner", "harmonic_accompanist"),
                ),
            )
        )

    def get(self, style_id: str) -> StylePack:
        try:
            return self._styles[style_id]
        except KeyError as error:
            raise KeyError(f"Unknown style pack: {style_id}") from error
