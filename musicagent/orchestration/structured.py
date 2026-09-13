"""Structured-output helpers for LLM-backed agent responses."""

from __future__ import annotations

import json
import re
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class CompleteFn(Protocol):
    """Minimal completion callable accepted by structured response generation."""

    def __call__(self, agent_id: str, prompt: str, model: str | None = None) -> str:
        """Return a completion for an agent prompt."""


class AgentStructuredOutput(BaseModel):
    """Validated machine-readable output from an agent task."""

    model_config = ConfigDict(frozen=True)

    agent_id: str
    summary: str
    sections: tuple[str, ...] = ()
    actions: tuple[str, ...] = ()
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class ParsedAgentOutput(BaseModel):
    """Parsed agent output with validation state and safe fallback data."""

    model_config = ConfigDict(frozen=True)

    valid: bool
    output: AgentStructuredOutput
    raw_response: str
    error: str | None = None


def build_structured_agent_prompt(agent_id: str, user_prompt: str) -> str:
    """Build a JSON-only prompt for machine-consumed agent output."""

    return chr(10).join(
        [
            "You are running inside MusicAgent.",
            f"Agent id: {agent_id}",
            "Return JSON only. Do not wrap it in markdown fences.",
            "The JSON object must contain:",
            '- "agent_id": string',
            '- "summary": string',
            '- "sections": array of strings',
            '- "actions": array of strings',
            '- "confidence": number between 0 and 1, or null',
            "",
            "User music brief:",
            user_prompt,
        ]
    )


def build_structured_repair_prompt(agent_id: str, raw_response: str) -> str:
    """Build a repair prompt that asks the model to convert malformed output to schema JSON."""

    return chr(10).join(
        [
            "Convert the following MusicAgent response into valid JSON only.",
            f"Agent id must be: {agent_id}",
            "Required keys: agent_id, summary, sections, actions, confidence.",
            "Use arrays of strings for sections and actions.",
            "Do not include markdown fences or commentary.",
            "",
            "Malformed response:",
            raw_response,
        ]
    )


def parse_agent_structured_output(agent_id: str, raw_response: str) -> ParsedAgentOutput:
    """Validate an agent response, falling back to safe structured metadata if invalid."""

    try:
        payload = json.loads(extract_json_object(raw_response))
        output = AgentStructuredOutput.model_validate(payload)
    except (json.JSONDecodeError, ValidationError, ValueError) as error:
        return ParsedAgentOutput(
            valid=False,
            output=AgentStructuredOutput(agent_id=agent_id, summary=raw_response),
            raw_response=raw_response,
            error=type(error).__name__,
        )

    if output.agent_id != agent_id:
        return ParsedAgentOutput(
            valid=False,
            output=AgentStructuredOutput(agent_id=agent_id, summary=output.summary),
            raw_response=raw_response,
            error="agent_id_mismatch",
        )
    return ParsedAgentOutput(valid=True, output=output, raw_response=raw_response)


def extract_json_object(raw_response: str) -> str:
    """Extract a JSON object from plain or fenced model output."""

    stripped = raw_response.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL)
    if fenced:
        return fenced.group(1)
    return stripped


def structured_output_to_markdown(parsed: ParsedAgentOutput) -> str:
    """Render structured output into human-readable markdown content."""

    output = parsed.output
    lines = [output.summary]
    if output.sections:
        lines.extend(["", "Sections:", *[f"- {section}" for section in output.sections]])
    if output.actions:
        lines.extend(["", "Actions:", *[f"- {action}" for action in output.actions]])
    if not parsed.valid:
        lines.extend(["", "Raw response:", parsed.raw_response])
    return chr(10).join(lines)


class StructuredAgentResponder:
    """Generate and validate structured agent output through a minimal LLM interface."""

    def __init__(self, max_repair_attempts: int = 1) -> None:
        self._max_repair_attempts = max_repair_attempts

    def generate(
        self,
        agent_id: str,
        user_prompt: str,
        complete: CompleteFn,
        model: str | None = None,
    ) -> ParsedAgentOutput:
        raw_response = complete(
            agent_id,
            build_structured_agent_prompt(agent_id, user_prompt),
            model=model,
        )
        parsed = parse_agent_structured_output(agent_id, raw_response)
        if parsed.valid:
            return parsed

        repaired = parsed
        for _ in range(self._max_repair_attempts):
            repair_response = complete(
                agent_id,
                build_structured_repair_prompt(agent_id, repaired.raw_response),
                model=model,
            )
            repaired = parse_agent_structured_output(agent_id, repair_response)
            if repaired.valid:
                return repaired
        return parsed
