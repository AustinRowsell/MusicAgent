# Phase 7 Decision-Gated Containerisation and Delivery Plan

## 1. Purpose

This plan addresses the unresolved open questions from the original multi-agent music creation plan before any further implementation work continues. It also defines how the MusicAgent system should be containerised, whether agents should run as separate containers, and what Docker Compose setup should exist for local development and rapid production.

No further feature implementation should happen until the decision log in this document is completed.

## 2. Why This Plan Exists

The previous plan contained open questions that materially affect architecture, dependencies, runtime topology, CLI behaviour, and user experience. Those questions should be resolved before extending the project further because they influence:

- Whether the CLI remains the primary interface or becomes secondary to a web UI.
- How generated MIDI files should be named and organised.
- Whether inputs are copied into project folders or referenced externally.
- Whether audio inputs are in scope soon.
- Which model/provider configuration is considered supported.
- Whether containerisation is single-service or multi-service.
- Whether agents are logical software roles inside one process or independently deployable services.

## 3. Current Implementation Baseline

The repository currently has:

- CLI project creation.
- Built-in crew registry.
- Two built-in crews:
  - `electronic_alt_pop`
  - `singer_songwriter_acoustic`
- Deterministic stub agent execution.
- Per-track/per-instrument MIDI export.
- Markdown, JSON, manifest, and MIDI output generation.
- Style pack creation workflow.
- Lyricist persona creation workflow.
- Project template and batch manifest workflow.
- Optional review pass.
- Local FastAPI web API.
- Tests, lint, formatting, and mypy validation.

The current implementation is a strong local prototype, but production/deployment decisions remain open.

## 4. Decision Log To Complete Before Next Implementation

| ID | Decision | Options | Recommended Default | Status |
| --- | --- | --- | --- | --- |
| D1 | Primary interface for next milestone | CLI-first, Web-first, Both equally | Both, but CLI remains canonical automation path | Answered: both equally |
| D2 | Generated MIDI target | General MIDI programs, descriptive track names only, both | Both: General MIDI program hints plus descriptive filenames | Answered: both |
| D3 | Input file handling | Copy into project folder, reference original paths, configurable | Copy by default; allow reference-only later | Answered: support copy and reference modes |
| D4 | Audio input scope | Defer, metadata only, audio-to-MIDI/transcription | Defer audio-to-MIDI; allow metadata-only later | Answered: support metadata-only audio handling while deferring transcription |
| D5 | Default LLM model/provider | OpenAI only, OpenAI-compatible, fully pluggable | OpenAI-compatible via LangChain | Answered: fully pluggable; no hard provider default |
| D6 | Output path policy | Absolute only, relative allowed, both | Both; resolve and record absolute root plus relative manifest paths | Answered: both relative and absolute paths supported |
| D7 | Electronic crew structure bias | Radio-pop, club, both via style packs | Both via style packs | Answered: style-pack selected with radio-pop and club variants supported |
| D8 | Acoustic accompaniment default | Guitar-first, piano-first, both | Both, chosen by style/template | Answered: guitar-first default |
| D9 | Agent runtime model | Logical agents in one app, one container per crew, one container per agent | Logical agents in one app for now; Compose services for app/web/worker later | Answered: support deployment profiles for one-app, per-crew, and per-agent modes |
| D10 | Containerisation requirement | No containers, app container only, Docker Compose stack | Docker Compose stack for local dev and reproducible runs | Answered: yes, add Docker/Compose next |
| D11 | Secrets/config approach in containers | `.env`, Docker secrets, external secret manager | `.env` for local only, never committed; env vars in Compose | Answered: use `.env.example` and ignored real `.env` for local config |
| D12 | Generated output mounting | Local bind mount, named volume, configurable | Local bind mount `./outputs:/app/outputs` | Answered: bind mount `./outputs` by default |

## 5. Containerisation Recommendation

### 5.1 Short Answer

Yes, the project should have a Compose file.

The containerisation design should support multiple deployment profiles because the preferred agent runtime can vary depending on where the system runs.

Required deployment profiles:

```text
Profile: app
├── musicagent-cli      # run one-off CLI commands and batch jobs
└── musicagent-web      # local FastAPI dashboard/API

Profile: crews
├── musicagent-web
├── electronic-alt-pop-crew
└── singer-songwriter-acoustic-crew

Profile: agents
├── musicagent-web
├── groove-architect-agent
├── sound-designer-agent
├── cyber-critic-agent
├── lyricist-poet-agent
├── topliner-agent
└── harmonic-accompanist-agent
```

### 5.2 Runtime Profile Guidance

Use the `app` profile for the fastest local development loop and simplest desktop usage.

Use the `crews` profile when different crews need separate scaling, resource limits, logs, or model settings.

Use the `agents` profile when individual agent roles need isolation, separate hardware, different dependencies, or independent scaling.

The code should keep agent boundaries explicit so all three profiles can use the same core contracts:

- `AgentRunner` abstraction.
- `CrewProjectGenerator` orchestration service.
- Prompt files per agent.
- Structured task outputs per agent.
- Registry-defined crews and agents.

### 5.3 Profile Implementation Strategy

The first Compose implementation should include all three profiles, even if `crews` and `agents` initially reuse the same image and command entrypoint. This gives deployment flexibility without prematurely duplicating code.

Recommended service approach:

- `musicagent-cli`: app profile, one-off CLI commands.
- `musicagent-web`: app/web profile, local dashboard and API.
- `electronic-alt-pop-crew`: crews profile, runs the electronic crew worker command.
- `singer-songwriter-acoustic-crew`: crews profile, runs the acoustic crew worker command.
- `groove-architect-agent`, `sound-designer-agent`, `cyber-critic-agent`, `lyricist-poet-agent`, `topliner-agent`, `harmonic-accompanist-agent`: agents profile, initially run lightweight worker entrypoints.

A queue service can be added later if asynchronous distributed work is required.

## 6. Proposed Docker Assets

### 6.1 Files To Add

```text
Dockerfile
compose.yaml
.dockerignore
docs/planning/containerisation-decisions.md
```

Optional later:

```text
compose.agent-services.yaml
compose.dev.yaml
scripts/docker-run-cli.sh
scripts/docker-run-web.sh
```

### 6.2 Dockerfile Goals

The Dockerfile should:

- Use a Python version compatible with the dependency set, currently Python 3.13 or 3.12.
- Install dependencies with `uv` or standard `pip` based on the selected team preference.
- Avoid copying `.env`, `.git`, `.venv`, outputs, and IDE files into the image.
- Run as a non-root user if practical.
- Support both CLI and web commands from the same image.
- Expose the FastAPI port only for the web service.

### 6.3 Compose Goals

The Compose file should:

- Provide a reusable `musicagent` image build.
- Run CLI one-off jobs.
- Run FastAPI web server.
- Mount project outputs to the host.
- Pass API keys and model config through environment variables only.
- Avoid hard-coding secrets.
- Use a local bind mount for generated outputs.

Example conceptual services:

```yaml
services:
  musicagent-cli:
    build: .
    profiles: ["cli"]
    env_file:
      - .env
    volumes:
      - ./outputs:/app/outputs
      - ./inputs:/app/inputs:ro
    command: ["musicagent", "crews"]

  musicagent-web:
    build: .
    profiles: ["web"]
    env_file:
      - .env
    volumes:
      - ./outputs:/app/outputs
      - ./inputs:/app/inputs:ro
    ports:
      - "8000:8000"
    command: ["uvicorn", "musicagent.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

This example should be expanded during implementation to include the selected `app`, `crews`, and `agents` profiles.

## 7. Phase 7 Implementation Scope

The decision log is now answered. The next implementation should add:

1. `.dockerignore` excluding `.env`, `.git`, `.venv`, `.idea`, caches, generated outputs, and local artifacts.
2. `Dockerfile` using Python 3.13 or 3.12 and the project dependency lock.
3. `compose.yaml` with profiles for:
   - `app`: `musicagent-cli` and `musicagent-web`.
   - `crews`: `electronic-alt-pop-crew` and `singer-songwriter-acoustic-crew`.
   - `agents`: one service per initial built-in agent.
4. `.env.example` with non-secret configuration names only.
5. Documentation for local container usage.
6. Tests or smoke checks that verify:
   - container builds;
   - CLI command runs in container;
   - web service starts in container;
   - output bind mount receives generated files under `./outputs`;
   - no `.env`, `.git`, `.venv`, `.idea`, or generated outputs are copied into the image.

The Compose implementation should support all selected runtime modes from the start, even if the per-crew and per-agent services initially share the same image and run lightweight worker-style commands.

## 8. Additional Product Decisions Captured

### 8.1 CLI vs Web Ownership

If CLI remains canonical, all web actions should call the same application services used by CLI. This is the recommended approach because it keeps automation and tests straightforward.

If web becomes primary, the CLI should become a thin wrapper around the same service layer.

### 8.2 MIDI Naming and General MIDI

The per-track MIDI rule is settled. The remaining decision is whether each file should include General MIDI program changes.

Recommended:

- File names remain descriptive: `drums.mid`, `bass.mid`, `vocal_melody.mid`.
- MIDI files include sensible General MIDI program hints where applicable.
- Drums use channel 10 / zero-based channel 9.

### 8.3 Input Copying

Recommended:

- Copy input files into the project folder by default for reproducibility.
- Record original source paths in manifest metadata when safe.
- Add a future `--reference-inputs` mode if desired.

### 8.4 Audio Inputs

Recommended:

- Keep audio-to-MIDI transcription out of scope for now.
- Add metadata-only audio support later if needed.
- Do not add heavy audio/ML dependencies until a concrete testable requirement exists.

### 8.5 Model Provider

Recommended:

- Keep `LangChainOpenAILLMClient` as one implementation.
- Keep `StubLLMClient` as the default in tests and offline mode.
- Add model/provider selection through configuration only after deciding the default provider.

## 9. Questions For User

Please answer these before the next implementation step:

1. Should the next milestone keep the CLI as the canonical interface, with the web UI as a wrapper, or should the web UI become the primary interface?
2. Should generated MIDI files include General MIDI program changes, or should they only use descriptive filenames/track names?
3. Should input files always be copied into each project folder, or should the tool support reference-only inputs from the start?
4. Should audio input support remain deferred, or do you want metadata-only audio file handling now?
5. Which model/provider should be the default for non-stub runs: OpenAI, any OpenAI-compatible endpoint, Azure OpenAI, or something else?
6. Should output paths support both relative and absolute paths, or should project output roots always be absolute?
7. For the electronic crew, should the default structure lean radio-pop, club/extended mix, or be selected through style packs?
8. For the acoustic crew, should the default accompaniment be guitar-first, piano-first, or selected through templates/style packs?
9. Do you want agents to remain logical roles inside one app container for now, or do you want one container per agent from the start?
10. Should I add Docker/Compose support next?
11. If yes, should Compose include both `musicagent-cli` and `musicagent-web` services?
12. Should generated outputs be bind-mounted to `./outputs` on the host by default?
13. Should `.env` be the local container config mechanism, with `.env.example` committed and real `.env` ignored?

## 10. Recommended Answers

If you want the fastest reliable path, choose:

1. CLI canonical; web wraps the same service layer.
2. General MIDI hints plus descriptive filenames.
3. Copy inputs by default.
4. Defer audio input beyond metadata-only.
5. OpenAI-compatible via LangChain; stub default for tests.
6. Support both, resolving roots internally.
7. Style-pack selected; default `electro_pop` for short songs.
8. Template/style-pack selected; default guitar-first.
9. Logical agents in one app container for now.
10. Yes, add Docker/Compose next.
11. Yes, include CLI and web services.
12. Yes, bind mount `./outputs:/app/outputs`.
13. Yes, use `.env.example` and keep `.env` ignored.
