from musicagent.registries.crews import BuiltInCrewRegistry


def test_built_in_crew_registry_exposes_initial_crews():
    registry = BuiltInCrewRegistry.default()

    assert registry.get("electronic_alt_pop").id == "electronic_alt_pop"
    assert registry.get("singer_songwriter_acoustic").id == "singer_songwriter_acoustic"


def test_style_aliases_resolve_to_built_in_crews():
    registry = BuiltInCrewRegistry.default()

    assert registry.resolve("indietronica").id == "electronic_alt_pop"
    assert registry.resolve("electro_pop").id == "electronic_alt_pop"
    assert registry.resolve("acoustic").id == "singer_songwriter_acoustic"
    assert registry.resolve("folk_acoustic").id == "singer_songwriter_acoustic"


def test_electronic_crew_includes_required_agents():
    crew = BuiltInCrewRegistry.default().get("electronic_alt_pop")

    assert crew.required_agents == (
        "groove_architect",
        "sound_designer",
        "cyber_critic",
    )


def test_singer_songwriter_crew_includes_required_agents():
    crew = BuiltInCrewRegistry.default().get("singer_songwriter_acoustic")

    assert crew.required_agents == (
        "lyricist_poet",
        "topliner",
        "harmonic_accompanist",
    )
