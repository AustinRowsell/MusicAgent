"""Task definitions and structured outputs for built-in crews."""

from __future__ import annotations

from dataclasses import dataclass

from musicagent.midi.events import MidiNote, MidiTrack
from musicagent.models import ProjectRequest
from musicagent.orchestration.structured import ParsedAgentOutput, structured_output_to_markdown


@dataclass(frozen=True)
class AgentTask:
    agent_id: str
    markdown_path: str
    data_path: str
    title: str


@dataclass(frozen=True)
class AgentTaskResult:
    agent_id: str
    markdown_path: str
    data_path: str
    markdown: str
    data: dict[str, object]


ELECTRONIC_TASKS: tuple[AgentTask, ...] = (
    AgentTask("groove_architect", "groove_plan.md", "data/groove_plan.json", "Groove Plan"),
    AgentTask("sound_designer", "sound_design.md", "data/synth_patches.json", "Sound Design"),
    AgentTask(
        "cyber_critic",
        "cyber_critic_review.md",
        "data/electronic_review.json",
        "Cyber Critic Review",
    ),
)

ACOUSTIC_TASKS: tuple[AgentTask, ...] = (
    AgentTask("lyricist_poet", "lyrics.md", "data/lyrics.json", "Lyrics"),
    AgentTask("topliner", "topline.md", "data/topline.json", "Topline"),
    AgentTask(
        "harmonic_accompanist", "accompaniment.md", "data/accompaniment.json", "Accompaniment"
    ),
)


def tasks_for_crew(crew_id: str) -> tuple[AgentTask, ...]:
    if crew_id == "singer_songwriter_acoustic":
        return ACOUSTIC_TASKS
    return ELECTRONIC_TASKS


def tracks_for_crew(crew_id: str) -> list[MidiTrack]:
    if crew_id == "singer_songwriter_acoustic":
        return [
            MidiTrack(
                name="vocal_melody",
                notes=(
                    MidiNote(pitch=64, start_beats=0, duration_beats=1, velocity=86),
                    MidiNote(pitch=67, start_beats=1, duration_beats=1, velocity=88),
                ),
                program=53,
            ),
            MidiTrack(
                name="accompaniment",
                notes=(
                    MidiNote(pitch=48, start_beats=0, duration_beats=2, velocity=72),
                    MidiNote(pitch=55, start_beats=0, duration_beats=2, velocity=68),
                    MidiNote(pitch=60, start_beats=0, duration_beats=2, velocity=66),
                ),
                program=25,
            ),
        ]
    return [
        MidiTrack(
            name="drums",
            notes=(
                MidiNote(pitch=36, start_beats=0, duration_beats=0.25, velocity=110, channel=9),
                MidiNote(pitch=38, start_beats=1, duration_beats=0.25, velocity=95, channel=9),
                MidiNote(pitch=42, start_beats=0.5, duration_beats=0.25, velocity=70, channel=9),
            ),
        ),
        MidiTrack(
            name="bass",
            notes=(MidiNote(pitch=45, start_beats=0, duration_beats=1, velocity=92),),
            program=38,
        ),
        MidiTrack(
            name="chords",
            notes=(
                MidiNote(pitch=57, start_beats=0, duration_beats=2, velocity=76),
                MidiNote(pitch=60, start_beats=0, duration_beats=2, velocity=72),
                MidiNote(pitch=64, start_beats=0, duration_beats=2, velocity=70),
            ),
            program=89,
        ),
        MidiTrack(
            name="hooks",
            notes=(MidiNote(pitch=72, start_beats=1, duration_beats=0.5, velocity=86),),
            program=81,
        ),
    ]


def build_task_result(
    task: AgentTask, request: ProjectRequest, agent_output: ParsedAgentOutput
) -> AgentTaskResult:
    """Build markdown and machine JSON data from validated structured agent output."""

    markdown = chr(10).join(
        [
            f"# {task.title}",
            "",
            f"Agent: {task.agent_id}",
            f"Crew: {request.crew}",
            f"Prompt: {request.prompt}",
            "",
            structured_output_to_markdown(agent_output),
            "",
        ]
    )
    data: dict[str, object] = {
        "agent_id": task.agent_id,
        "crew": request.crew,
        "prompt": request.prompt,
        "summary": agent_output.output.summary,
        "sections": list(agent_output.output.sections),
        "actions": list(agent_output.output.actions),
        "confidence": agent_output.output.confidence,
        "structured_output_valid": agent_output.valid,
        "structured_output_error": agent_output.error,
    }
    return AgentTaskResult(
        agent_id=task.agent_id,
        markdown_path=task.markdown_path,
        data_path=task.data_path,
        markdown=markdown,
        data=data,
    )


def build_stub_task_result(
    task: AgentTask, request: ProjectRequest, llm_response: str
) -> AgentTaskResult:
    """Backward-compatible helper for existing tests and deterministic flows."""

    return build_task_result(
        task,
        request,
        ParsedAgentOutput.model_validate(
            {
                "valid": True,
                "output": {
                    "agent_id": task.agent_id,
                    "summary": llm_response,
                    "sections": (),
                    "actions": (),
                    "confidence": None,
                },
                "raw_response": llm_response,
            }
        ),
    )
