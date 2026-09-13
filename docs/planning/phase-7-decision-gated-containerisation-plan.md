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

- Use Python 3.14, matching the local toolchain and project metadata.
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

## 7. Multi-Phase Implementation Roadmap

The decision log is now answered, but implementation should not be treated as a single Docker task. The work should be delivered through the following quality-gated phases so the captured product and runtime decisions are not lost.

### Phase 7.1: Decision Codification and Configuration Contracts

Goal: turn the answered decisions into explicit code/configuration contracts before adding Docker runtime files.

Deliverables:

- Add a typed configuration model for runtime decisions:
  - interface mode: CLI and web are both first-class;
  - MIDI metadata mode: descriptive names plus General MIDI hints;
  - input handling mode: copy or reference;
  - audio handling mode: metadata-only, no transcription;
  - model provider mode: fully pluggable, no hard default;
  - output path mode: relative and absolute paths supported;
  - electronic structure mode: style-pack selected, with radio-pop and club variants;
  - acoustic accompaniment default: guitar-first;
  - deployment profile: app, crew, or agent.
- Add `.env.example` with non-secret configuration names only.
- Add config documentation for local CLI, web, and container runs.
- Add tests proving config defaults and overrides are loaded without secrets.

Quality gate:

- Tests must prove `.env` is not required for offline/stub operation.
- Tests must prove real secret values are never written into generated manifests or logs.
- `ruff`, `mypy`, and full `pytest` must pass.

### Phase 7.2: Output Path, Input Mode, and Audio Metadata Support

Goal: implement the decisions around input handling, output path policy, and metadata-only audio handling.

Deliverables:

- Support both relative and absolute output roots consistently across CLI and web API.
- Record resolved output root and relative generated asset paths in manifests.
- Add explicit input handling mode:
  - copy input files into project folders;
  - reference input files without copying;
  - configurable default, with copy as the safe default.
- Add metadata-only audio input support for common audio file extensions such as `.wav`, `.mp3`, `.aiff`, `.aif`, `.flac`, and `.ogg`.
- Do not add audio-to-MIDI transcription or heavy ML/audio dependencies in this phase.
- Add manifest metadata for referenced/copied inputs, including type, original path when safe, project-local path when copied, and detected extension.

Quality gate:

- Tests must cover copy mode and reference mode.
- Tests must cover relative output paths and absolute output paths.
- Tests must cover audio metadata-only ingestion without transcription.
- Tests must verify generated outputs still use per-track/per-instrument MIDI files.

### Phase 7.3: MIDI Metadata and Style-Pack Defaults

Goal: implement General MIDI hints and the selected style/accompaniment defaults without weakening the per-track MIDI rule.

Deliverables:

- Add General MIDI program hints to MIDI tracks where applicable.
- Keep descriptive filenames and track names as the primary human-facing organisation method.
- Keep drums on zero-based channel 9 / General MIDI channel 10.
- Add or extend style packs for:
  - electronic radio-pop structure;
  - electronic club/extended structure;
  - acoustic guitar-first structure.
- Ensure electronic structure is selected through style packs rather than hard-coded crew branching.
- Ensure acoustic defaults are guitar-first while still allowing piano or alternate templates later.

Quality gate:

- Tests must verify MIDI files contain expected program changes for non-drum tracks where applicable.
- Tests must verify drums use channel 9.
- Tests must verify radio-pop and club electronic styles produce different section/structure metadata.
- Tests must verify acoustic default metadata is guitar-first.
- Tests must verify no single `full_sketch.mid` is required or generated as the primary output.

### Phase 7.4: Pluggable Model Provider Architecture

Goal: make model/provider selection fully pluggable before enabling real non-stub execution paths.

Deliverables:

- Add an explicit provider registry or factory for LLM clients.
- Keep `StubLLMClient` as the default for tests and offline execution.
- Keep `LangChainOpenAILLMClient` as one provider implementation, not the hard-coded default.
- Allow provider selection by config/environment, for example:
  - `MUSICAGENT_LLM_PROVIDER=stub`
  - `MUSICAGENT_LLM_PROVIDER=openai-compatible`
  - `MUSICAGENT_LLM_PROVIDER=azure-openai`
- Add validation for required environment variables by selected provider.
- Ensure missing credentials fail clearly without printing secret values.

Quality gate:

- Tests must prove stub mode requires no credentials.
- Tests must prove provider-specific missing config is reported without leaking secrets.
- Tests must prove CLI and web use the same provider selection path.
- Tests must not make live network/model calls.

### Phase 7.5: Container Build Foundation

Goal: add a secure, reproducible container image before adding multi-profile Compose complexity.

Deliverables:

- Add `.dockerignore` excluding:
  - `.env`
  - `.git`
  - `.venv`
  - `.idea`
  - `outputs`
  - Python caches
  - test caches
  - local editor/system files.
- Add `Dockerfile` using Python 3.14, consistent with `requires-python = ">=3.14,<3.15"`.
- Install dependencies from the project lock/config.
- Support both CLI and web commands from the same image.
- Avoid copying generated outputs or local secrets into the image.
- Prefer a non-root runtime user where practical.

Quality gate:

- Docker build must pass.
- Container CLI smoke test must list crews.
- Container CLI smoke test must create per-track MIDI outputs under mounted `./outputs`.
- Image context must exclude `.env`, `.git`, `.venv`, `.idea`, and generated outputs.

### Phase 7.6: Compose App Profile

Goal: support the simplest local container runtime first.

Deliverables:

- Add `compose.yaml` with an `app` profile containing:
  - `musicagent-cli` for one-off commands;
  - `musicagent-web` for FastAPI local dashboard/API.
- Bind mount:
  - `./outputs:/app/outputs`;
  - `./inputs:/app/inputs:ro` when present.
- Use `.env.example` for documented local configuration names.
- Use real `.env` only locally and keep it ignored.
- Expose web API on `localhost:8000` by default.

Quality gate:

- `docker compose --profile app run --rm musicagent-cli crews` must work.
- `docker compose --profile app run --rm musicagent-cli create ... --dry-run` must write to host `./outputs`.
- `docker compose --profile app up musicagent-web` must start the API.
- Web API `/api/crews` must respond from the container.

### Phase 7.7: Compose Crew Profile

Goal: support deployment where each crew can run separately.

Deliverables:

- Extend `compose.yaml` with a `crews` profile containing:
  - `electronic-alt-pop-crew`;
  - `singer-songwriter-acoustic-crew`.
- Each service should use the same image initially but set explicit environment/config for its crew id.
- Each service should run a lightweight worker or command loop placeholder that can later be attached to a queue.
- Do not duplicate business logic per container.

Quality gate:

- Both crew services must start successfully.
- Each crew service must expose or log its configured crew id without secrets.
- A smoke command for each crew must generate expected crew-specific outputs.

### Phase 7.8: Compose Agent Profile

Goal: support deployment where individual agents can run separately.

Deliverables:

- Extend `compose.yaml` with an `agents` profile containing one service for each initial agent:
  - `groove-architect-agent`;
  - `sound-designer-agent`;
  - `cyber-critic-agent`;
  - `lyricist-poet-agent`;
  - `topliner-agent`;
  - `harmonic-accompanist-agent`.
- Each service should use the same image initially but set explicit environment/config for its agent id.
- Agent services should be lightweight placeholders until queue-based distributed orchestration is introduced.
- Preserve the same `AgentRunner` and task output contracts used by app and crew profiles.

Quality gate:

- All agent services must start successfully.
- Each agent service must expose or log its configured agent id without secrets.
- Tests or smoke checks must prove the service list covers all six initial built-in agents.

### Phase 7.9: Documentation and Operator Workflows

Goal: make the containerised system usable without reading the source code.

Deliverables:

- Add container usage documentation covering:
  - CLI local run;
  - web local run;
  - app profile;
  - crew profile;
  - agent profile;
  - output mount behaviour;
  - `.env.example` usage;
  - no-secret policy;
  - troubleshooting common Docker/Compose issues.
- Add examples for:
  - creating an electronic project;
  - creating an acoustic project;
  - running a batch manifest;
  - opening the web dashboard;
  - downloading MIDI assets.

Quality gate:

- Documentation commands must be copy-paste runnable or clearly marked as examples.
- Documentation must not include real secrets.
- Documentation must explicitly state that per-agent containers are deployment profiles, not separate code forks.

### Phase 7.10: Final End-to-End Verification

Goal: prove the completed delivery is safe, reproducible, and aligned with all decisions.

Required checks:

- `uv run python -m pytest -q`
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run mypy musicagent`
- Docker build smoke test.
- Compose app profile CLI smoke test.
- Compose app profile web smoke test.
- Compose crew profile smoke test.
- Compose agent profile smoke test.
- Host `./outputs` bind mount verification.
- `.dockerignore` verification that secrets and generated outputs are excluded.

Completion criteria:

- All checks pass.
- All decisions D1-D12 are represented in code, config, docs, or tests.
- No real credentials are printed, stored, or committed.
- No single combined MIDI file is required as the main deliverable.
- CLI and web remain equally supported through shared service code.

## 8. Decision Traceability Matrix

| Decision | Implementation Phase(s) | Required Evidence |
| --- | --- | --- |
| D1: CLI and web both first-class | 7.6, 7.9, 7.10 | CLI and web smoke tests pass using shared services |
| D2: General MIDI plus names | 7.3, 7.10 | MIDI tests inspect program/channel metadata and filenames |
| D3: Copy and reference input modes | 7.2, 7.10 | Tests cover copied and reference-only inputs |
| D4: Metadata-only audio, no transcription | 7.2, 7.10 | Tests cover audio metadata extraction without transcription dependencies |
| D5: Fully pluggable model provider | 7.4, 7.10 | Provider factory tests and no required hard default |
| D6: Relative and absolute output paths | 7.2, 7.10 | Tests cover both path forms and manifest paths |
| D7: Electronic style-pack structure variants | 7.3, 7.10 | Radio-pop and club style tests |
| D8: Guitar-first acoustic default | 7.3, 7.10 | Acoustic default metadata test |
| D9: App, crew, and agent runtime profiles | 7.6, 7.7, 7.8, 7.10 | Compose services and profile smoke tests |
| D10: Docker/Compose next | 7.5, 7.6, 7.7, 7.8 | Dockerfile and compose.yaml exist and build/run |
| D11: `.env.example`, ignored `.env` | 7.1, 7.5, 7.6, 7.9 | `.env.example`, `.gitignore`, `.dockerignore`, no secrets |
| D12: `./outputs` bind mount | 7.6, 7.10 | Compose smoke test writes host outputs |

## 9. Additional Product Decisions Captured

### 9.1 CLI vs Web Ownership

CLI and web are both first-class. Both interfaces should call the same application services so they remain feature-equivalent and avoid divergent business logic.

### 9.2 MIDI Naming and General MIDI

The per-track MIDI rule is settled. The remaining decision is whether each file should include General MIDI program changes.

Recommended:

- File names remain descriptive: `drums.mid`, `bass.mid`, `vocal_melody.mid`.
- MIDI files include sensible General MIDI program hints where applicable.
- Drums use channel 10 / zero-based channel 9.

### 9.3 Input Copying

Decision:

- Support both copy and reference modes.
- Copy input files into the project folder by default for reproducibility.
- Record original source paths in manifest metadata when safe.
- Add `--reference-inputs` or equivalent config support.

### 9.4 Audio Inputs

Decision:

- Support metadata-only audio handling.
- Keep audio-to-MIDI transcription out of scope for now.
- Do not add heavy audio/ML dependencies until a concrete testable requirement exists.

### 9.5 Model Provider

Decision:

- Model providers are fully pluggable with no hard default for real non-stub runs.
- Keep `LangChainOpenAILLMClient` as one provider implementation.
- Keep `StubLLMClient` as the default in tests and offline mode.
- Add model/provider selection through configuration.

## 10. Answered Questions Record

These questions have already been answered and are retained for traceability:

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

## 11. Actual Answers To Implement

1. CLI and web UI are both first-class.
2. MIDI should use both descriptive filenames/track names and General MIDI hints.
3. Input handling should support both copied inputs and reference-only inputs.
4. Audio support should include metadata-only handling while deferring audio-to-MIDI transcription.
5. Model/provider selection should be fully pluggable with no hard real-provider default.
6. Output roots should support both relative and absolute paths.
7. Electronic structure should be selected through style packs, with radio-pop and club/extended variants supported.
8. Acoustic accompaniment should default to guitar-first.
9. Runtime should support app, per-crew, and per-agent deployment profiles.
10. Docker/Compose should be added next.
11. Compose should include CLI and web services and expand to crew/agent profiles.
12. Generated outputs should bind mount to `./outputs` on the host by default.
13. Local container config should use committed `.env.example`; real `.env` remains ignored and must never be committed.
