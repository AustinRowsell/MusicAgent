from musicagent.orchestration.structured import (
    StructuredAgentResponder,
    build_structured_agent_prompt,
    parse_agent_structured_output,
    structured_output_to_markdown,
)


def test_structured_prompt_requests_json_only():
    prompt = build_structured_agent_prompt("lyricist_poet", "write a chorus")

    assert "Return JSON only" in prompt
    assert '"summary"' in prompt
    assert "lyricist_poet" in prompt


def test_parse_agent_structured_output_accepts_fenced_json():
    fence = chr(96) * 3
    newline = chr(10)
    raw_response = (
        fence
        + "json"
        + newline
        + '{"agent_id":"topliner","summary":"hook","sections":["chorus"],'
        + '"actions":["rise"],"confidence":0.9}'
        + newline
        + fence
    )

    parsed = parse_agent_structured_output("topliner", raw_response)

    assert parsed.valid is True
    assert parsed.output.summary == "hook"
    assert parsed.output.sections == ("chorus",)
    assert "Actions:" in structured_output_to_markdown(parsed)


def test_parse_agent_structured_output_falls_back_for_invalid_json():
    parsed = parse_agent_structured_output("topliner", "plain prose")

    assert parsed.valid is False
    assert parsed.output.summary == "plain prose"
    assert parsed.error == "JSONDecodeError"


def test_structured_responder_repairs_malformed_output_once():
    calls: list[str] = []

    def complete(agent_id: str, prompt: str, model: str | None = None) -> str:
        calls.append(prompt)
        if len(calls) == 1:
            return "not json"
        return '{"agent_id":"lyricist_poet","summary":"fixed","sections":[],"actions":[],"confidence":0.8}'

    parsed = StructuredAgentResponder().generate(
        "lyricist_poet", "write a chorus", complete, model="mistral-nemo:12b"
    )

    assert parsed.valid is True
    assert parsed.output.summary == "fixed"
    assert len(calls) == 2
    assert "Convert the following" in calls[1]
