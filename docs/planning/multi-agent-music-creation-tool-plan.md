# Multi-Agent Music Creation Tool Plan

## 1. Vision

Build a Python-based multi-agent music creation tool that helps users rapidly produce musical ideas, arrangements, MIDI files, and project-ready assets from multiple input materials. The system will use **CrewAI** for agent orchestration, **LangChain OpenAI** for LLM access, and **Mido** for MIDI generation, transformation, and export.

The tool should feel like a practical production assistant rather than a chat-only demo: users provide musical direction and source materials, the system assigns work to specialised agents, and outputs are written predictably into user-selected folders.

## 2. Goals

- Provide an easy-to-use interface for fast musical ideation and production.
- Accept multiple input materials in a single session.
- Assign different inputs and tasks to specialised music agents.
- Generate structured outputs such as MIDI, arrangement notes, chord charts, lyrics, prompts, and production briefs.
- Allow users to choose output folders per project, stem, track, or asset type.
- Keep the architecture extensible so additional agents, models, and output formats can be added later.
- Avoid exposing API keys or secrets in logs, generated files, or committed configuration.

## 3. Non-Goals for the First Version

- Real-time audio synthesis or full DAW replacement.
- Commercial-quality mastering.
- Direct plugin hosting such as VST/AU support.
- Automatic copyrighted song cloning.
- Cloud collaboration or user account management.
- Advanced audio-to-MIDI transcription unless explicitly added later.

## 4. Target Users

- Producers who want quick MIDI sketches and arrangement ideas.
- Songwriters who want lyrics, chord progressions, and song structures.
- Composers who want multi-agent orchestration assistance.
- Developers experimenting with AI-assisted music workflows.
- Content creators needing rapid background music concepts.

## 5. Core User Experience

A user should be able to run the tool, create or select a project, provide several input materials, choose a production goal, and receive organised outputs in a chosen folder.

Example flow:

1. User starts the app.
2. User creates a project named `late-night-house-demo`.
3. User adds inputs:
   - Text prompt: `deep house track with warm chords and a vocal chop feel`.
   - Reference notes file: `references/energy.md`.
   - MIDI bassline: `inputs/bassline.mid`.
   - Chord idea: `Am7 Fmaj7 Cmaj7 G6`.
4. User chooses output folder: `~/Music/AI Projects/late-night-house-demo`.
5. System assigns tasks:
   - Brief agent interprets direction.
   - Harmony agent develops chords.
   - Rhythm agent creates drum and groove plans.
   - Melody agent creates lead/hook material.
   - Arrangement agent builds sections.
   - MIDI agent writes `.mid` files with Mido.
   - Review agent checks musical consistency.
6. Tool writes output files:
   - `brief.md`
   - `arrangement.md`
   - `chords.mid`
   - `bass.mid`
   - `melody.mid`
   - `drums.mid`
   - `full_sketch.mid`
   - `session_manifest.json`

## 6. Proposed Interface

### 6.1 Initial Interface: CLI Wizard

The first interface should be a guided CLI because it is fast to build, easy to test, and suitable for producer workflows.

Recommended command:

```bash
musicagent create
```

Wizard prompts:

- Project name.
- Output folder.
- Style or genre.
- Tempo.
- Key or mode.
- Time signature.
- Desired duration or number of sections.
- Input materials to include.
- Which assets to generate.
- Whether to run a review/refinement pass.

### 6.2 Fast Mode

For rapid production, support a single-command mode:

```bash
musicagent create 
  --name late-night-house-demo 
  --prompt "deep house track with warm chords" 
  --tempo 124 
  --key "A minor" 
  --input inputs/bassline.mid 
  --input references/energy.md 
  --output "~/Music/AI Projects/late-night-house-demo"
```

### 6.3 Future Interface: Local Web UI

A later version can add a lightweight local web interface with:

- Project dashboard.
- Drag-and-drop input materials.
- Agent assignment controls.
- Output folder picker.
- Regenerate buttons per part.
- MIDI preview and download links.

Recommended future stack: FastAPI backend with a simple React or vanilla HTML/CSS frontend.

## 7. Input Materials

The system should support a normalised input model so agents can consume different materials consistently.

### 7.1 Supported First-Version Inputs

- Text prompt.
- Plain text notes.
- Markdown briefs.
- Chord progressions entered as text.
- MIDI files.
- JSON project manifests.

### 7.2 Later Inputs

- Audio files for reference metadata extraction.
- Lyrics documents.
- MusicXML.
- DAW export metadata.
- Folder-based batch imports.

### 7.3 Input Metadata

Each input should be represented as an `InputMaterial` object with:

- `id`
- `type`
- `path` when file-based
- `content` when text-based
- `description`
- `assigned_agents`
- `priority`
- `constraints`

Example manifest:

```json
{
  "inputs": [
    {
      "id": "main_prompt",
      "type": "text_prompt",
      "content": "cinematic ambient track with piano and soft strings",
      "assigned_agents": ["brief", "harmony", "arrangement"],
      "priority": "high"
    },
    {
      "id": "existing_bassline",
      "type": "midi",
      "path": "inputs/bassline.mid",
      "assigned_agents": ["rhythm", "midi"],
      "priority": "medium"
    }
  ]
}
```

## 8. Agent Design

### 8.1 Project Brief Agent

Responsibilities:

- Interpret the user prompt and input materials.
- Produce a concise creative brief.
- Identify genre, mood, tempo, instrumentation, structure, and constraints.
- Resolve conflicting instructions.

Outputs:

- `brief.md`
- structured `ProjectBrief` data.

### 8.2 Music Theory / Harmony Agent

Responsibilities:

- Create or refine chord progressions.
- Suggest key, mode, harmonic rhythm, substitutions, and voicings.
- Adapt harmony to the genre and emotional direction.

Outputs:

- `harmony.md`
- chord progression data.
- optional `chords.mid`.

### 8.3 Rhythm and Groove Agent

Responsibilities:

- Design drum patterns and rhythmic feel.
- Interpret tempo, swing, groove, and genre conventions.
- Create percussion lane plans for MIDI generation.

Outputs:

- `rhythm.md`
- drum pattern data.
- optional `drums.mid`.

### 8.4 Melody and Hook Agent

Responsibilities:

- Generate motifs, hooks, top-line ideas, and counter-melodies.
- Respect key, scale, phrase length, and arrangement sections.
- Provide call-and-response or variation ideas.

Outputs:

- `melody.md`
- melody event data.
- optional `melody.mid`.

### 8.5 Arrangement Agent

Responsibilities:

- Build a song structure.
- Assign musical parts to intro, verse, chorus, bridge, drop, outro, or custom sections.
- Decide energy curve and instrumentation changes.

Outputs:

- `arrangement.md`
- structured section map.

### 8.6 MIDI Production Agent

Responsibilities:

- Convert structured musical ideas into valid MIDI files using Mido.
- Merge parts into a full sketch.
- Set tempo, tracks, programs, channels, note lengths, velocities, and markers.

Outputs:

- individual `.mid` files.
- `full_sketch.mid`.
- `midi_report.md`.

### 8.7 Review and Refinement Agent

Responsibilities:

- Check consistency across brief, harmony, rhythm, melody, and arrangement.
- Flag contradictions or weak spots.
- Optionally request one refinement pass from specific agents.

Outputs:

- `review.md`
- revised structured data when refinement is enabled.

## 9. CrewAI Workflow

Recommended crew flow:

1. `ProjectBriefTask`
2. `InputAnalysisTask`
3. Parallel conceptual tasks:
   - `HarmonyTask`
   - `RhythmTask`
   - `MelodyTask`
4. `ArrangementTask`
5. `MidiGenerationTask`
6. `ReviewTask`
7. Optional `RevisionTask`
8. `ExportTask`

The orchestration layer should keep agent outputs structured. Free-form prose is useful for human-readable documentation, but downstream MIDI generation should consume validated Python data models.

## 10. LangChain OpenAI Usage

Use LangChain OpenAI as the model provider abstraction.

Implementation principles:

- Read model configuration from environment variables or a local ignored config file.
- Never hard-code API keys.
- Keep prompts versioned in source files.
- Prefer structured output parsing for agent hand-offs.
- Add retry and timeout handling.
- Include token/cost logging without recording secret values or complete private prompts unless explicitly configured.

Suggested model config fields:

- `OPENAI_API_KEY`
- `MUSICAGENT_MODEL`
- `MUSICAGENT_TEMPERATURE`
- `MUSICAGENT_MAX_TOKENS`

## 11. Mido MIDI Layer

The MIDI layer should be isolated from agent orchestration.

Recommended modules:

- `musicagent/midi/writer.py`
- `musicagent/midi/events.py`
- `musicagent/midi/scales.py`
- `musicagent/midi/chords.py`
- `musicagent/midi/drums.py`

Responsibilities:

- Convert notes, chords, and drum events into Mido messages.
- Handle ticks per beat, tempo conversion, and track naming.
- Validate note ranges and durations.
- Write deterministic output files.
- Provide simple utilities for merging tracks.

Suggested first MIDI data model:

```python
@dataclass(frozen=True)
class MidiNote:
    pitch: int
    start_beats: float
    duration_beats: float
    velocity: int
    channel: int = 0
```

## 12. Output Folder Design

The user should be able to specify a root output directory. Each project run should create a timestamped or named project folder.

Example output tree:

```text
late-night-house-demo/
├── session_manifest.json
├── brief.md
├── arrangement.md
├── harmony.md
├── rhythm.md
├── melody.md
├── review.md
├── midi/
│   ├── chords.mid
│   ├── bass.mid
│   ├── drums.mid
│   ├── melody.mid
│   └── full_sketch.mid
├── data/
│   ├── project_brief.json
│   ├── arrangement.json
│   ├── harmony.json
│   ├── rhythm.json
│   └── melody.json
└── inputs/
    └── copied_or_referenced_inputs.json
```

Output rules:

- Never overwrite existing project folders unless `--overwrite` is explicitly provided.
- Write a manifest for every run.
- Record relative paths to generated files.
- Support `--output` for root folder selection.
- Support `--asset-output midi=...` later for per-asset folder overrides.

## 13. Proposed Project Structure

```text
musicagent/
├── __init__.py
├── cli.py
├── config.py
├── models.py
├── orchestration/
│   ├── __init__.py
│   ├── crew.py
│   ├── agents.py
│   └── tasks.py
├── prompts/
│   ├── brief.md
│   ├── harmony.md
│   ├── rhythm.md
│   ├── melody.md
│   ├── arrangement.md
│   └── review.md
├── midi/
│   ├── __init__.py
│   ├── writer.py
│   ├── chords.py
│   ├── drums.py
│   └── scales.py
├── io/
│   ├── __init__.py
│   ├── inputs.py
│   ├── outputs.py
│   └── manifest.py
└── tests/
    ├── test_inputs.py
    ├── test_outputs.py
    ├── test_midi_writer.py
    └── test_cli.py
```

## 14. Configuration

Configuration should support both environment variables and project-level config files.

Suggested config file:

```toml
[model]
provider = "openai"
model = "gpt-4o-mini"
temperature = 0.7

[defaults]
tempo = 120
key = "C major"
time_signature = "4/4"
output_root = "./outputs"
review_pass = true
```

Local secrets should remain outside version control. If a `.env` file is used, ensure it is ignored by Git.

## 15. Dependency Plan

Candidate dependencies:

- `crewai` for multi-agent orchestration.
- `langchain-openai` for OpenAI model integration.
- `mido` for MIDI file generation.
- `pydantic` for structured validation.
- `typer` or `argparse` for CLI interface.
- `rich` for readable CLI output.
- `pytest` for tests.

Before implementation, verify dependency licenses and project compatibility. Do not introduce GPL or commercial-only dependencies without explicit approval.

## 16. Testing Strategy

### 16.1 Unit Tests

- Input parsing from prompts, files, and MIDI metadata.
- Output folder creation and overwrite protection.
- Manifest writing.
- MIDI event generation.
- MIDI file validity checks using Mido.
- Agent task construction without live API calls.

### 16.2 Integration Tests

- CLI dry run creates expected folder tree.
- Stubbed LLM responses produce deterministic MIDI output.
- Multiple input materials are assigned to expected agents.
- Existing output folder is protected unless overwrite is enabled.

### 16.3 Manual Validation

- Run a simple prompt-only project.
- Run a project with text plus MIDI input.
- Import generated MIDI into a DAW.
- Confirm file naming and folder selection are intuitive.

## 17. Implementation Phases

### Phase 1: Foundation

- Replace sample script with package structure.
- Add CLI entry point.
- Add configuration loading.
- Add typed models for project requests, input materials, agent assignments, and outputs.
- Add output folder and manifest writer.
- Add tests for config, inputs, and outputs.

### Phase 2: MIDI Core

- Add Mido dependency after license/compatibility verification.
- Implement MIDI note/event model.
- Implement basic chord, melody, bass, and drum writers.
- Generate deterministic MIDI from structured test data.
- Add MIDI unit tests.

### Phase 3: Agent Orchestration

- Add CrewAI and LangChain OpenAI after license/compatibility verification.
- Implement agents and task definitions.
- Add prompt files.
- Add stub mode for tests and offline development.
- Add structured output validation.

### Phase 4: End-to-End Project Generation

- Wire CLI to crew workflow.
- Support multiple inputs.
- Support explicit output folder selection.
- Write markdown, JSON, and MIDI outputs.
- Add integration tests with mocked LLM calls.

### Phase 5: Rapid Production Features

- Add presets by genre.
- Add regeneration for individual parts.
- Add project templates.
- Add batch mode from a manifest file.
- Add optional refinement pass.

### Phase 6: Optional UI

- Add local web interface.
- Add drag-and-drop input selection.
- Add generated asset browser.
- Add MIDI preview/download workflow.

## 18. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| LLM output is inconsistent | Use structured schemas and validation. |
| MIDI output is musically poor | Start with constrained generation rules and review pass. |
| API costs become high | Add dry-run/stub mode, model config, and token limits. |
| Output folders are overwritten | Default to safe creation and require explicit overwrite. |
| Agents become too abstract | Keep each agent tied to concrete file/data outputs. |
| Secrets leak into logs | Redact config and never print environment variable values. |
| Dependency incompatibility with Python 3.14 | Verify package support before implementation; consider lowering Python requirement if needed. |

## 19. Open Questions

- Should the primary interface be CLI-only for v1, or should a local web UI be included immediately?
- Should generated MIDI target General MIDI instruments or custom track labels only?
- Should the system copy input files into the project folder or reference them by path?
- Should the tool support audio inputs in v1 or defer them?
- Which OpenAI-compatible model should be the default?
- Should output folders be absolute-only, or should relative project paths be allowed?

## 20. Recommended First Milestone

Implement a CLI-first MVP that can:

1. Accept a prompt, tempo, key, one or more input files, and an output folder.
2. Create a safe project output tree.
3. Use stubbed agent responses to generate deterministic structured music data.
4. Write markdown summaries and valid MIDI files.
5. Run tests without requiring OpenAI credentials.

After that baseline is reliable, connect CrewAI and LangChain OpenAI behind the same structured interfaces.
