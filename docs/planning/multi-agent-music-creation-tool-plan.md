# Multi-Agent Music Creation Tool Plan

## 1. Vision

Build a Python-based multi-agent music creation tool that helps users rapidly produce musical ideas, arrangements, MIDI files, and project-ready assets from multiple input materials. The system will use **CrewAI** for agent orchestration, **LangChain OpenAI** for LLM access, and **Mido** for MIDI generation, transformation, and export.

The tool should feel like a practical production assistant rather than a chat-only demo: users provide musical direction and source materials, the system assigns work to specialised agents, and outputs are written predictably into user-selected folders.

## 2. Goals

- Provide an easy-to-use interface for fast musical ideation and production.
- Accept multiple input materials in a single session.
- Assign different inputs and tasks to specialised music agents.
- Generate structured outputs such as per-track/per-instrument MIDI files, arrangement notes, chord charts, lyrics, prompts, and production briefs.
- Require each track or instrument part to be exported as its own MIDI file; the system must not rely on one combined MIDI file as the main arrangement deliverable.
- Allow users to choose output folders per project, stem, track, or asset type.
- Keep the architecture extensible so additional agents, models, and output formats can be added later.
- Make lyricist personas, genre/style packs, musical rule sets, and production templates pluggable so new creative directions can be added without rewriting the core workflow.
- Follow SOLID design principles across package structure, orchestration boundaries, MIDI generation, configuration, and I/O.
- Treat Test-Driven Development (TDD) as mandatory: failing tests should be written before implementation for every production feature or bug fix.
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
   - optional `preview_full_sketch.mid` for reference only
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
- Export every track or instrument as its own standalone MIDI file.
- Optionally create a combined preview MIDI for quick listening/reference, but this must never replace the required per-track/per-instrument files.
- Set tempo, tracks, programs, channels, note lengths, velocities, and markers.

Outputs:

- required individual `.mid` files for each track/instrument.
- optional `preview_full_sketch.mid` for reference only.
- `midi_report.md`.

### 8.7 Review and Refinement Agent

Responsibilities:

- Check consistency across brief, harmony, rhythm, melody, and arrangement.
- Flag contradictions or weak spots.
- Optionally request one refinement pass from specific agents.

Outputs:

- `review.md`
- revised structured data when refinement is enabled.

### 8.8 Lyricist Agent Extension Point

Lyric writing should be modelled as an extensible family of agents rather than a single hard-coded lyric generator. Different lyricists can represent different creative voices, writing constraints, languages, rhyme densities, narrative structures, and genre conventions.

First-version lyricist support can include a generic `LyricistAgent`, but the design should allow later additions such as:

- Pop hook lyricist.
- Rap verse lyricist.
- Folk storyteller lyricist.
- Ambient spoken-word lyricist.
- Children's song lyricist.
- Multilingual lyricist.
- Brand-safe/commercial lyricist.

Each lyricist implementation should declare:

- Supported styles or genres.
- Input requirements.
- Output schema.
- Safety and originality constraints.
- Whether it writes full lyrics, hooks only, topline phrases, or revision suggestions.

Outputs:

- `lyrics.md`
- structured lyric section data.
- optional syllable, rhyme, and phrasing metadata for melody alignment.

### 8.9 Style and Genre Pack Extension Point

Music styles should be represented as configurable style packs, not scattered conditionals in agent prompts or MIDI code. A style pack should describe the reusable musical assumptions for a genre or production direction.

A style pack can define:

- Tempo ranges.
- Common keys, modes, scales, and chord vocabulary.
- Drum pattern templates.
- Bass movement rules.
- Instrumentation defaults.
- Arrangement conventions.
- Groove, swing, velocity, and humanisation defaults.
- Recommended agent set, including optional lyricist personas.
- Prompt fragments for each relevant agent.

Example style pack names:

- `deep_house`
- `lofi_hip_hop`
- `cinematic_ambient`
- `pop_ballad`
- `trap`
- `synthwave`
- `folk_acoustic`

Style packs should be loaded through a registry so adding a new style normally means adding a new configuration file and tests, not modifying the core project generation workflow.

## 9. Initial Built-In Crews

The first implementation should ship with a useful range of built-in crew members rather than a generic placeholder crew. These crews must be available out of the box through the crew registry and selectable from the CLI by name or style alias.

The initial crews are not examples only; they are part of the initial product scope and must be implemented with prompts, schemas, deterministic stub outputs, and tests.

### 9.1 Electronic / Alternative Pop / Electro Pop / Indietronica Crew

Registry id: `electronic_alt_pop`

Style aliases:

- `electronic`
- `alternative_pop`
- `alt_pop`
- `electro_pop`
- `indietronica`

Primary purpose:

Create modern electronic and alternative pop sketches with strong rhythmic identity, detailed synth direction, and structurally effective builds, drops, and energy movement.

Expected inputs:

- User prompt or creative brief.
- Tempo, key, and time signature when supplied.
- Optional MIDI references for drums, bass, melody, or chords.
- Optional reference notes describing era, artist-adjacent direction, instrumentation, or production mood.
- Optional style pack such as `deep_house`, `synthwave`, `electro_pop`, or `indietronica`.

Expected outputs:

- `brief.md`
- `electronic_arrangement.md`
- `groove_plan.md`
- `sound_design.md`
- `cyber_critic_review.md`
- `midi/drums.mid`
- `midi/bass.mid`
- `midi/chords.mid`
- `midi/hooks.mid`
- optional `midi/preview_full_sketch.mid` for reference only.
- structured JSON data for groove, synth patches, arrangement sections, and review findings.

#### 9.1.1 Groove Architect Agent

Agent id: `groove_architect`

Responsibilities:

- Focus strictly on the rhythm section.
- Calculate syncopated drum placements for kicks, snares, claps, hats, percussion, and ghost hits.
- Define sidechain trigger timing and intensity recommendations.
- Produce bar-aware drum patterns suitable for 4-bar, 8-bar, and 16-bar phrases.
- Vary groove density across intro, verse, pre-chorus, chorus, drop, bridge, and outro sections.
- Provide MIDI-ready rhythmic event data with beat positions, durations, velocities, lanes, and humanisation hints.

Constraints:

- Must not rewrite lyrics, melody, or harmony except to note rhythmic compatibility issues.
- Must expose enough structured data for deterministic drum MIDI generation.
- Must respect tempo, time signature, requested style pack, and arrangement section lengths.

Outputs:

- `groove_plan.md`
- `data/groove_plan.json`
- rhythm event data for `midi/drums.mid` and sidechain marker data.

#### 9.1.2 Sound Designer Agent

Agent id: `sound_designer`

Responsibilities:

- Specialise in subtractive and wavetable synthesis direction.
- Describe exact synth parameters based on requested era and style, including oscillator waveshapes, detune, filter cutoff, resonance, envelope settings, LFO routing, modulation targets, unison, glide, effects, and macro controls.
- Provide separate patch guidance for bass, pads, plucks, leads, arps, effects, and vocal-chop-like textures where relevant.
- Translate subjective direction such as `warm`, `glassy`, `gritty`, `80s`, `bloghouse`, `hyper-clean`, or `washed out` into concrete synthesis settings.

Constraints:

- Must produce DAW-agnostic patch descriptions rather than relying on one commercial synth plugin.
- Must keep parameters structured so future exporters can map them to plugin presets or automation lanes.
- Must not generate MIDI notes unless explicitly delegated through a MIDI task.

Outputs:

- `sound_design.md`
- `data/synth_patches.json`
- optional automation recommendations for filter sweeps, risers, sidechain feel, and modulation movement.

#### 9.1.3 Cyber Critic Agent

Agent id: `cyber_critic`

Responsibilities:

- Analyse the overall arrangement and production structure.
- Check whether build-ups, drops, transitions, fills, and breakdowns happen at musically appropriate bar intervals such as 4-bar, 8-bar, 16-bar, or 32-bar phrases.
- Evaluate the structural energy curve across the full track.
- Identify sections that feel too static, too crowded, underdeveloped, or mistimed.
- Recommend targeted revisions for groove, sound design, harmony, melody, or arrangement agents.

Constraints:

- Must report issues as actionable notes tied to bar numbers or section names.
- Must avoid vague criticism; every finding should include an expected fix.
- Must preserve the user's creative direction unless there is a clear structural conflict.

Outputs:

- `cyber_critic_review.md`
- `data/electronic_review.json`
- optional revision requests routed to specific agents.

### 9.2 Singer-Songwriter / Acoustic Crew

Registry id: `singer_songwriter_acoustic`

Style aliases:

- `singer_songwriter`
- `singer-songwriter`
- `acoustic`
- `folk_acoustic`
- `acoustic_pop`

Primary purpose:

Create emotionally coherent song sketches centred on lyrics, vocal melody, and supportive acoustic harmony.

Expected inputs:

- User prompt or lyrical theme.
- Optional existing lyrics, poem fragments, titles, diary-style notes, or story outline.
- Optional key, tempo, vocal range, time signature, and target song form.
- Optional chord ideas or MIDI sketches.
- Optional style pack such as `folk_acoustic`, `pop_ballad`, or `acoustic_pop`.

Expected outputs:

- `brief.md`
- `lyrics.md`
- `topline.md`
- `accompaniment.md`
- `acoustic_arrangement.md`
- `midi/vocal_melody.mid`
- `midi/accompaniment.mid`
- optional `midi/preview_full_sketch.mid` for reference only.
- structured JSON data for lyrics, syllable mapping, melody contour, chords, accompaniment patterns, and arrangement sections.

#### 9.2.1 Lyricist / Poet Agent

Agent id: `lyricist_poet`

Responsibilities:

- Generate or refine lyrics with deep attention to classic songwriting tropes, metaphor generation, imagery, emotional weight, and narrative movement.
- Support complex rhyme schemes, internal rhyme, repeated motifs, contrast sections, and title-focused hooks.
- Shape lyrics around theme, perspective, emotional arc, and section function.
- Produce lyrics that are original and avoid direct imitation of living artists or copyrighted songs.

Constraints:

- Must keep lyrics aligned to the requested mood, style, and audience.
- Must provide section labels such as verse, pre-chorus, chorus, bridge, refrain, or outro.
- Must include optional notes on rhyme scheme, imagery, and narrative intent.

Outputs:

- `lyrics.md`
- `data/lyrics.json`
- optional rhyme, syllable, stress, and theme metadata.

#### 9.2.2 Topliner Agent

Agent id: `topliner`

Responsibilities:

- Take raw lyrics and plan the vocal melody line.
- Assign syllable weights, phrase lengths, breaths, rests, and structural pauses.
- Target specific note intervals within the chosen musical scale to make the vocal memorable and singable.
- Identify hook notes, leap moments, repeated motifs, and cadence targets.
- Produce MIDI-ready vocal melody data that aligns with lyric syllables.

Constraints:

- Must respect the requested vocal range when supplied.
- Must preserve lyric intelligibility and avoid overloading weak syllables.
- Must produce structured phrase data suitable for `midi/vocal_melody.mid`.

Outputs:

- `topline.md`
- `data/topline.json`
- vocal melody event data and syllable-to-note mapping.

#### 9.2.3 Harmonic Accompanist Agent

Agent id: `harmonic_accompanist`

Responsibilities:

- Design open-voiced acoustic guitar patterns or piano chord movements that explicitly support the mood of the lyrics.
- Use extensions, suspensions, inversions, pedal tones, passing chords, and voicing changes where musically appropriate.
- Match accompaniment density to the vocal and lyrical emotional arc.
- Provide strumming, picking, comping, or piano pattern suggestions by section.

Constraints:

- Must prioritise support for the lyric and topline over harmonic complexity.
- Must keep chord choices playable or clearly mark advanced voicings.
- Must produce structured chord and accompaniment data suitable for MIDI generation.

Outputs:

- `accompaniment.md`
- `data/accompaniment.json`
- chord and accompaniment event data for `midi/accompaniment.mid`.

### 9.3 Built-In Crew Registry Requirements

The crew registry should expose these initial crews as stable built-ins:

- `electronic_alt_pop`
- `singer_songwriter_acoustic`

Each built-in crew should declare:

- `id`
- display name
- style aliases
- required agents
- optional agents
- accepted input types
- produced output types
- default style pack
- compatible style packs
- default task graph
- validation rules

Adding a new crew later should require adding a crew definition, prompts/configuration, and tests. It should not require modifying the CLI command handler, MIDI writer internals, or core orchestration workflow.

## 10. CrewAI Workflow

Recommended generic crew flow:

1. `ProjectBriefTask`
2. `InputAnalysisTask`
3. Crew-specific parallel conceptual tasks, such as:
   - `GrooveArchitectTask`
   - `SoundDesignerTask`
   - `HarmonyTask`
   - `LyricistTask`
   - `ToplineTask`
   - `MelodyTask`
4. Crew-specific arrangement or accompaniment tasks.
5. `MidiGenerationTask`
6. Crew-specific critique or review task.
7. Optional `RevisionTask`
8. `ExportTask`

The orchestration layer should keep agent outputs structured. Free-form prose is useful for human-readable documentation, but downstream MIDI generation should consume validated Python data models.

## 11. LangChain OpenAI Usage

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

## 12. MIDI and Music Analysis Layer

The MIDI and music analysis layer should be isolated from agent orchestration. The MVP should use `mido`, `pretty_midi`, and `music21` from the start, with each library assigned a clear responsibility.

Recommended modules:

- `musicagent/midi/writer.py`
- `musicagent/midi/events.py`
- `musicagent/midi/analyser.py`
- `musicagent/theory/scales.py`
- `musicagent/theory/chords.py`
- `musicagent/theory/harmony.py`
- `musicagent/midi/drums.py`

Responsibilities:

- Use `mido` for deterministic low-level MIDI writing, message construction, tempo events, track names, and final `.mid` export.
- Export each arrangement part as a separate MIDI file per track/instrument, for example `drums.mid`, `bass.mid`, `chords.mid`, `lead.mid`, `vocal_melody.mid`, or `accompaniment.mid`.
- Do not use a single all-in-one MIDI file as the primary output. A combined `preview_full_sketch.mid` may be generated only as an optional reference asset.
- Use `pretty_midi` for higher-level MIDI inspection, imported MIDI analysis, generated-note validation, instrument-track analysis, and future transformation workflows.
- Use `music21` for theory-aware validation of keys, scales, chords, intervals, harmonic movement, voice-leading checks, and notation-style reasoning.
- Convert notes, chords, and drum events into validated symbolic event data before writing MIDI messages.
- Handle ticks per beat, tempo conversion, and track naming.
- Validate note ranges, durations, harmony, and scale fit.
- Write deterministic output files.
- Provide simple utilities for optional preview-only merged tracks.

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

## 13. Output Folder Design

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
│   ├── lead.mid
│   └── preview_full_sketch.mid  # optional reference only
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
- Store every instrument or track part as a separate MIDI file.
- Treat any combined `preview_full_sketch.mid` as optional reference output only, never as the only arrangement export.
- Support `--output` for root folder selection.
- Support `--asset-output midi=...` later for per-asset folder overrides.

## 14. Proposed Project Structure

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
├── registries/
│   ├── __init__.py
│   ├── agents.py
│   ├── crews.py
│   ├── lyricists.py
│   └── styles.py
├── styles/
│   ├── electronic_alt_pop.toml
│   ├── electro_pop.toml
│   ├── indietronica.toml
│   ├── singer_songwriter_acoustic.toml
│   ├── folk_acoustic.toml
│   ├── deep_house.toml
│   ├── lofi_hip_hop.toml
│   └── cinematic_ambient.toml
├── prompts/
│   ├── brief.md
│   ├── groove_architect.md
│   ├── sound_designer.md
│   ├── cyber_critic.md
│   ├── lyricist_poet.md
│   ├── topliner.md
│   ├── harmonic_accompanist.md
│   ├── harmony.md
│   ├── rhythm.md
│   ├── melody.md
│   ├── lyrics.md
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
    ├── test_crew_registry.py
    ├── test_electronic_alt_pop_crew.py
    ├── test_singer_songwriter_acoustic_crew.py
    └── test_cli.py
```

## 15. SOLID Architecture Requirements

The implementation should be designed around SOLID principles from the first production commit, not retrofitted later.

### 15.1 Single Responsibility Principle

Each module and class should have one clear reason to change:

- CLI modules should parse user intent and delegate work, not generate music directly.
- Agent orchestration should coordinate tasks, not write MIDI files or manage folders.
- MIDI modules should translate validated musical data into MIDI, not call LLMs.
- I/O modules should read inputs and write outputs, not contain music theory rules.
- Configuration modules should load and validate settings, not run application workflows.

### 15.2 Open/Closed Principle

The system should be open to new agents, input types, output formats, lyricist personas, and music styles without modifying core workflow code repeatedly.

Recommended approach:

- Use protocols or abstract base classes for input readers, output writers, agent runners, lyricist agents, style packs, and MIDI exporters.
- Register new handlers through explicit factories or registries.
- Prefer adding a new implementation or style configuration over editing large conditional blocks.
- Keep style-specific prompt fragments, tempo ranges, instrumentation defaults, and groove rules in style pack data.
- Keep lyricist-specific voice, form, rhyme, and language rules behind a lyricist registry.

### 15.3 Liskov Substitution Principle

Alternative implementations should be interchangeable:

- A stub LLM runner should be usable anywhere a real LangChain OpenAI runner is expected.
- A dry-run MIDI writer should be usable anywhere the Mido writer is expected.
- File-based input readers should follow the same contract as text-based input readers.

### 15.4 Interface Segregation Principle

Interfaces should stay small and role-specific:

- Agents should not depend on file-system APIs unless their role explicitly requires file access.
- MIDI writers should not depend on CrewAI types.
- CLI code should depend on application services, not low-level implementation classes.
- Test doubles should only need to implement the methods required by the behaviour under test.

### 15.5 Dependency Inversion Principle

High-level workflow code should depend on abstractions rather than concrete tools:

- The project generation workflow should depend on an `AgentRunner` abstraction, not directly on CrewAI.
- The model layer should depend on an `LLMClient` abstraction, not directly on LangChain OpenAI.
- The MIDI workflow should depend on a `MidiWriter` abstraction, not directly on Mido message construction.
- The output workflow should depend on an `OutputStore` abstraction, not hard-coded local paths.

This separation is essential for TDD because tests must be able to run with deterministic fakes and without OpenAI credentials.

## 16. Configuration

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

## 17. Dependency and Tooling Plan

The implementation should use a small, explicit dependency set that supports the planned architecture without coupling the domain model to vendor-specific APIs. Dependencies should be added only when they are needed by a tested feature.

### 17.1 Required Runtime Python Libraries

- `crewai`: multi-agent crew orchestration and task coordination.
- `langchain-openai`: OpenAI-compatible LLM integration through LangChain abstractions.
- `mido`: deterministic low-level MIDI file creation, reading, validation, event manipulation, and export.
- `pretty_midi`: higher-level MIDI inspection, imported MIDI analysis, generated-note validation, and musical transformation support.
- `music21`: music-theory analysis for keys, scales, chords, intervals, harmonic movement, and notation-style reasoning.
- `pydantic`: structured data models, schema validation, and agent output parsing.
- `typer`: CLI interface for wizard and fast-command workflows.
- `rich`: readable terminal output, progress display, tables, panels, and error messages.
- `python-dotenv`: local development loading of `.env` files without committing secrets.

### 17.2 Required Development and Test Libraries

- `pytest`: primary test runner for TDD.
- `pytest-cov`: coverage reporting for unit and integration tests.
- `pytest-mock`: clean mocking support for LLM clients, agent runners, MIDI writers, and output stores.
- `ruff`: linting and formatting for fast feedback.
- `mypy`: static type checking.

### 17.3 Standard-Library Tools to Prefer Before Adding Dependencies

Use Python standard library modules where they are sufficient:

- `argparse` only if `typer` is later rejected; do not use both for the main CLI.
- `dataclasses` for simple immutable MIDI/domain value objects when Pydantic validation is not needed.
- `pathlib` for paths.
- `json` for manifest and structured output files.
- `tomllib` for reading TOML config on Python versions that support it.
- `logging` for application logging with secret redaction.
- `unittest.mock` where it is clearer than `pytest-mock`.

### 17.4 Optional Future Libraries

These should not be added to the MVP unless a failing test or accepted feature requires them:

- `fastapi`: future local web API.
- `uvicorn`: future local web server for FastAPI.
- `python-multipart`: future file uploads in a web UI.

### 17.5 Project Tooling Commands

The project should define repeatable commands in `pyproject.toml` or documented scripts for:

- Install/sync dependencies.
- Run all tests.
- Run a focused test file or test case.
- Run coverage.
- Run formatting.
- Run linting.
- Run type checking.
- Run the CLI in dry-run/stub mode without OpenAI credentials.

Expected validation command set once implemented:

```bash
pytest
pytest --cov=musicagent
ruff format .
ruff check .
mypy musicagent
musicagent create --crew electronic_alt_pop --prompt "test" --output outputs/test-electronic --dry-run
musicagent create --crew singer_songwriter_acoustic --prompt "test" --output outputs/test-acoustic --dry-run
```

### 17.6 Dependency Compatibility Checks

Before adding dependencies to `pyproject.toml`, verify:

- Package supports the selected Python version. The current project requires Python `>=3.14`, which may be ahead of some ecosystem support; if required packages do not support Python 3.14 yet, consider lowering the project requirement to a stable supported version such as Python 3.12 or 3.13.
- Package license is acceptable. Do not introduce GPL or commercial-only dependencies without explicit human approval.
- Package is actively maintained enough for production use.
- Package is already necessary for a tested feature, not speculative future work.

### 17.7 Initial Dependency Recommendation

For the first implementation pass, plan to add:

```toml
dependencies = [
  "crewai",
  "langchain-openai",
  "mido",
  "music21",
  "pretty_midi",
  "pydantic",
  "python-dotenv",
  "rich",
  "typer",
]

[dependency-groups]
dev = [
  "mypy",
  "pytest",
  "pytest-cov",
  "pytest-mock",
  "ruff",
]
```

Exact versions should be pinned or constrained only after compatibility and license checks have been completed.

## 18. Testing Strategy

TDD is mandatory for this project. Every production feature or bug fix should start with a failing automated test that describes the desired behaviour. Implementation should then be limited to the smallest clean change that makes the test pass, followed by refactoring while keeping the suite green.

### 18.1 TDD Workflow

For each feature:

1. Write a failing unit or integration test first.
2. Run the focused test and confirm the expected failure.
3. Implement the smallest production change that satisfies the test.
4. Run the focused test and confirm it passes.
5. Refactor toward SOLID boundaries if needed.
6. Run the relevant test group, then the full suite before considering the work complete.

### 18.2 Unit Tests

- Input parsing from prompts, files, and MIDI metadata.
- Output folder creation and overwrite protection.
- Manifest writing.
- MIDI event generation.
- MIDI file validity checks using Mido.
- Per-track/per-instrument MIDI export tests that fail if the only output is a single combined arrangement file.
- Agent task construction without live API calls.
- SOLID boundary tests using fakes for LLM clients, agent runners, MIDI writers, and output stores.
- Style pack loading, validation, and selection.
- Lyricist registry lookup and substitution.
- Adding a new lyricist or style without modifying core orchestration tests.
- Built-in crew registry exposes `electronic_alt_pop` and `singer_songwriter_acoustic`.
- Electronic crew includes `groove_architect`, `sound_designer`, and `cyber_critic`.
- Singer-songwriter crew includes `lyricist_poet`, `topliner`, and `harmonic_accompanist`.

### 18.3 Integration Tests

- CLI dry run creates expected folder tree.
- Stubbed LLM responses produce deterministic MIDI output.
- Multiple input materials are assigned to expected agents.
- Existing output folder is protected unless overwrite is enabled.
- End-to-end workflow succeeds without OpenAI credentials by using deterministic stubs.
- Selecting different style packs changes generated structure while preserving the same workflow contract.
- Selecting different lyricist personas changes lyric output while preserving the same lyric schema.
- Selecting `electronic_alt_pop` runs the Groove Architect, Sound Designer, and Cyber Critic tasks and writes their expected outputs.
- Selecting `singer_songwriter_acoustic` runs the Lyricist / Poet, Topliner, and Harmonic Accompanist tasks and writes their expected outputs.

### 18.4 Manual Validation

- Run a simple prompt-only project.
- Run a project with text plus MIDI input.
- Run one project with `--crew electronic_alt_pop`.
- Run one project with `--crew singer_songwriter_acoustic`.
- Import generated MIDI into a DAW.
- Confirm file naming and folder selection are intuitive.

## 19. Implementation Phases

### Phase 1: Foundation

- Replace sample script with package structure.
- Add CLI entry point.
- Add configuration loading.
- Add typed models for project requests, input materials, agent assignments, crew definitions, style packs, and outputs.
- Add output folder and manifest writer.
- Add registries for crews, agents, lyricist personas, and style packs.
- Add the `electronic_alt_pop` and `singer_songwriter_acoustic` crew definitions to the built-in registry.
- Add tests for config, inputs, outputs, registry loading, style selection, and the two initial built-in crews.

### Phase 2: MIDI and Music Analysis Core

- Add `mido`, `pretty_midi`, and `music21` dependencies after license and compatibility verification.
- Implement MIDI note/event model.
- Implement basic chord, melody, bass, and drum writers with `mido`.
- Implement per-track/per-instrument MIDI exports as the required output model.
- Implement optional preview-only merged MIDI generation without making it the primary deliverable.
- Implement imported/generated MIDI inspection with `pretty_midi`.
- Implement key, scale, chord, interval, and harmony validation with `music21`.
- Generate deterministic MIDI from structured test data.
- Add MIDI, MIDI-analysis, per-track export, and music-theory unit tests.

### Phase 3: Agent Orchestration

- Add CrewAI and LangChain OpenAI after license/compatibility verification.
- Implement agents and task definitions.
- Implement the Electronic / Alternative Pop / Electro Pop / Indietronica crew task graph.
- Implement the Singer-Songwriter / Acoustic crew task graph.
- Add prompt files for Groove Architect, Sound Designer, Cyber Critic, Lyricist / Poet, Topliner, and Harmonic Accompanist.
- Add stub mode for tests and offline development.
- Add structured output validation.

### Phase 4: End-to-End Project Generation

- Wire CLI to crew workflow.
- Support `--crew electronic_alt_pop` and `--crew singer_songwriter_acoustic`.
- Support style aliases that resolve to the correct built-in crew.
- Support multiple inputs.
- Support explicit output folder selection.
- Write markdown, JSON, and MIDI outputs.
- Add integration tests with mocked LLM calls.

### Phase 5: Rapid Production Features

- Add presets by genre.
- Add style pack creation workflow for new genres and subgenres.
- Add lyricist persona creation workflow for new writing voices and lyrical forms.
- Add regeneration for individual parts.
- Add project templates.
- Add batch mode from a manifest file.
- Add optional refinement pass.

### Phase 6: Optional UI

- Add local web interface.
- Add drag-and-drop input selection.
- Add generated asset browser.
- Add MIDI preview/download workflow.

## 20. Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| LLM output is inconsistent | Use structured schemas and validation. |
| MIDI output is musically poor | Start with constrained generation rules and review pass. |
| API costs become high | Add dry-run/stub mode, model config, and token limits. |
| Output folders are overwritten | Default to safe creation and require explicit overwrite. |
| Agents become too abstract | Keep each agent tied to concrete file/data outputs. |
| Initial crews are too generic | Define concrete agent contracts, output schemas, and tests for each built-in crew member. |
| Style expansion creates core-code churn | Use registries and style pack configuration rather than hard-coded branching. |
| Secrets leak into logs | Redact config and never print environment variable values. |
| Dependency incompatibility with Python 3.14 | Verify package support before implementation; consider lowering Python requirement if needed. |

## 21. Open Questions

- Should the primary interface be CLI-only for v1, or should a local web UI be included immediately?
- Should generated MIDI target General MIDI instruments or custom track labels only?
- Should the system copy input files into the project folder or reference them by path?
- Should the tool support audio inputs in v1 or defer them?
- Which OpenAI-compatible model should be the default?
- Should output folders be absolute-only, or should relative project paths be allowed?
- Should the initial electronic crew prioritise radio-pop song structures, club structures, or allow both through style packs?
- Should the initial acoustic crew support both guitar-first and piano-first accompaniment by default?

## 22. Recommended First Milestone

Implement a CLI-first MVP that can:

1. Accept a prompt, tempo, key, one or more input files, an output folder, and a selected crew.
2. Create a safe project output tree.
3. Use stubbed agent responses to generate deterministic structured music data.
4. Register and select the two initial crews: `electronic_alt_pop` and `singer_songwriter_acoustic`.
5. Write markdown summaries and valid per-track/per-instrument MIDI files.
6. Run tests without requiring OpenAI credentials.

After that baseline is reliable, connect CrewAI and LangChain OpenAI behind the same structured interfaces.

## 23. Initial Crew Creation Checklist

The following built-in crews have been created in this plan and must exist in the initial implementation scope:

- [x] `electronic_alt_pop`: Electronic / Alternative Pop / Electro Pop / Indietronica crew.
  - [x] `groove_architect`: rhythm-section specialist for syncopated drums, sidechain triggers, kicks, snares, and hats.
  - [x] `sound_designer`: subtractive and wavetable synthesis specialist for concrete synth parameter direction.
  - [x] `cyber_critic`: arrangement critic for build-ups, drops, phrase timing, and structural energy curve.
- [x] `singer_songwriter_acoustic`: Singer-Songwriter / Acoustic crew.
  - [x] `lyricist_poet`: lyric and poetry specialist for theme, metaphor, emotional weight, narrative, and complex rhyme.
  - [x] `topliner`: vocal melody planner for syllable weight, phrasing pauses, scale intervals, and catchiness.
  - [x] `harmonic_accompanist`: acoustic guitar or piano accompaniment specialist for open voicings, extensions, suspensions, and lyric-supportive harmony.
