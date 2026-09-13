"""Built-in crew registry."""

from __future__ import annotations

from dataclasses import dataclass

from musicagent.models import CrewDefinition, InputMaterialType


@dataclass(frozen=True)
class BuiltInCrewRegistry:
    """Registry for built-in crews and their aliases."""

    _crews: dict[str, CrewDefinition]
    _aliases: dict[str, str]

    @classmethod
    def default(cls) -> BuiltInCrewRegistry:
        electronic = CrewDefinition(
            id="electronic_alt_pop",
            display_name="Electronic / Alternative Pop / Electro Pop / Indietronica Crew",
            style_aliases=(
                "electronic",
                "alternative_pop",
                "alt_pop",
                "electro_pop",
                "indietronica",
            ),
            required_agents=("groove_architect", "sound_designer", "cyber_critic"),
            accepted_input_types=(
                InputMaterialType.TEXT_PROMPT,
                InputMaterialType.TEXT,
                InputMaterialType.MARKDOWN,
                InputMaterialType.MIDI,
                InputMaterialType.JSON,
            ),
            produced_output_types=(
                "brief",
                "electronic_arrangement",
                "groove_plan",
                "sound_design",
                "cyber_critic_review",
                "midi_per_track",
            ),
            default_style_pack="electronic_alt_pop",
            compatible_style_packs=(
                "electronic_alt_pop",
                "electro_pop",
                "indietronica",
                "deep_house",
                "synthwave",
            ),
            default_task_graph=(
                "project_brief",
                "input_analysis",
                "groove_architect",
                "sound_designer",
                "arrangement",
                "midi_generation",
                "cyber_critic",
                "export",
            ),
        )
        acoustic = CrewDefinition(
            id="singer_songwriter_acoustic",
            display_name="Singer-Songwriter / Acoustic Crew",
            style_aliases=(
                "singer_songwriter",
                "singer-songwriter",
                "acoustic",
                "folk_acoustic",
                "acoustic_pop",
            ),
            required_agents=("lyricist_poet", "topliner", "harmonic_accompanist"),
            accepted_input_types=(
                InputMaterialType.TEXT_PROMPT,
                InputMaterialType.TEXT,
                InputMaterialType.MARKDOWN,
                InputMaterialType.MIDI,
                InputMaterialType.JSON,
            ),
            produced_output_types=(
                "brief",
                "lyrics",
                "topline",
                "accompaniment",
                "acoustic_arrangement",
                "midi_per_track",
            ),
            default_style_pack="singer_songwriter_acoustic",
            compatible_style_packs=(
                "singer_songwriter_acoustic",
                "folk_acoustic",
                "pop_ballad",
                "acoustic_pop",
            ),
            default_task_graph=(
                "project_brief",
                "input_analysis",
                "lyricist_poet",
                "topliner",
                "harmonic_accompanist",
                "arrangement",
                "midi_generation",
                "export",
            ),
        )
        crews = {electronic.id: electronic, acoustic.id: acoustic}
        aliases = {crew.id: crew.id for crew in crews.values()}
        for crew in crews.values():
            aliases.update({alias: crew.id for alias in crew.style_aliases})
        return cls(_crews=crews, _aliases=aliases)

    def get(self, crew_id: str) -> CrewDefinition:
        try:
            return self._crews[crew_id]
        except KeyError as error:
            raise KeyError(f"Unknown crew: {crew_id}") from error

    def resolve(self, crew_or_alias: str) -> CrewDefinition:
        try:
            return self.get(self._aliases[crew_or_alias])
        except KeyError as error:
            raise KeyError(f"Unknown crew or style alias: {crew_or_alias}") from error

    def list(self) -> tuple[CrewDefinition, ...]:
        return tuple(self._crews.values())
