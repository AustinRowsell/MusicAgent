"""Built-in agent registry."""

from __future__ import annotations

from musicagent.models import AgentDefinition

_BUILT_IN_AGENTS: tuple[AgentDefinition, ...] = (
    AgentDefinition(
        id="groove_architect",
        display_name="Groove Architect",
        role="Rhythm-section specialist",
        responsibilities=("syncopated drums", "sidechain triggers", "kick/snare/hat patterns"),
    ),
    AgentDefinition(
        id="sound_designer",
        display_name="Sound Designer",
        role="Subtractive and wavetable synthesis specialist",
        responsibilities=("oscillators", "filter cutoff", "resonance", "LFO routing"),
    ),
    AgentDefinition(
        id="cyber_critic",
        display_name="Cyber Critic",
        role="Arrangement and energy-curve critic",
        responsibilities=("bar interval checks", "build/drop timing", "energy curve"),
    ),
    AgentDefinition(
        id="lyricist_poet",
        display_name="Lyricist / Poet",
        role="Lyrics, metaphor, narrative, and rhyme specialist",
        responsibilities=("theme", "metaphor", "emotional weight", "complex rhyme"),
    ),
    AgentDefinition(
        id="topliner",
        display_name="Topliner",
        role="Vocal melody planner",
        responsibilities=("syllable weights", "phrasing", "scale intervals", "hooks"),
    ),
    AgentDefinition(
        id="harmonic_accompanist",
        display_name="Harmonic Accompanist",
        role="Acoustic guitar and piano accompaniment specialist",
        responsibilities=("open voicings", "extensions", "suspensions", "lyric support"),
    ),
)


def built_in_agents() -> tuple[AgentDefinition, ...]:
    return _BUILT_IN_AGENTS
