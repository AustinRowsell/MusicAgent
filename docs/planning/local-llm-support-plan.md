# Local LLM Support Plan

## 1. Purpose

MusicAgent has a requirement that local LLM execution must be available without real OpenAI credentials. The target architecture is a repo-managed Docker stack where MusicAgent containers talk to a local model-server container through an OpenAI-compatible API.

This document is now the canonical plan for the **remaining** local LLM work. It also records the implementation baseline already present in the working tree so future work does not duplicate completed changes.

## 2. Current implementation baseline

The following work is already present in the working tree and must not be planned again as new work.

### 2.1 Runtime configuration already supports model routing

`musicagent/config.py` now supports:

- default provider: `MUSICAGENT_LLM_PROVIDER`;
- default model: `MUSICAGENT_MODEL`;
- OpenAI-compatible base URL: `MUSICAGENT_OPENAI_BASE_URL`;
- low-resource model: `MUSICAGENT_LOW_RESOURCE_MODEL`;
- low-resource switch: `MUSICAGENT_USE_LOW_RESOURCE_MODEL`;
- per-agent model overrides via `MUSICAGENT_AGENT_MODEL_<AGENT_ID>`.

Example per-agent variables:

```env
MUSICAGENT_AGENT_MODEL_LYRICIST_POET=mistral-nemo:12b
MUSICAGENT_AGENT_MODEL_TOPLINER=mistral-nemo:12b
MUSICAGENT_AGENT_MODEL_CYBER_CRITIC=qwen2.5:14b
MUSICAGENT_AGENT_MODEL_REVIEWER=qwen2.5:14b
```

### 2.2 LLM abstraction already supports per-call model selection

`musicagent/orchestration/llm.py` now includes:

- `LLMClient` protocol;
- `AgentModelRouter`;
- `create_agent_model_router(settings)`;
- OpenAI-compatible client support for per-call model overrides;
- provider construction from typed settings and environment values;
- missing configuration errors that report variable names, not values.

### 2.3 Crew generation already uses configured LLM clients by default

`musicagent/orchestration/crew.py` now includes:

- `LLMAgentRunner`;
- `create_configured_agent_runner()`;
- `CrewProjectGenerator()` defaulting to the configured provider path;
- explicit injection support for tests via `agent_runner=...`;
- deterministic stub mode remaining available and credential-free.

### 2.4 Docker Compose local-LLM profile already exists

`compose.yaml` now includes:

- `ollama` service;
- `musicagent-local-llm-cli` service;
- `musicagent-local-llm-web` service;
- `ollama-models` persistent volume;
- local endpoint wiring to `http://ollama:11434/v1`;
- local placeholder API key wiring for Ollama's OpenAI-compatible API;
- default/per-agent/low-resource model environment variables.

`compose.local-certs.yaml` is an optional override for networks that intercept TLS or require a local certificate authority when Ollama pulls from `registry.ollama.ai`. Local-LLM helper scripts enable that override only when `./certs` contains `.crt` or `.pem` files; otherwise the base Compose stack has no certificate mount or `SSL_CERT_DIR` override. The `certs/` directory is ignored by Git and excluded from Docker build contexts.

### 2.5 Helper scripts and docs already exist

The working tree now includes helper scripts for Dockerised local LLM workflows:

```bash
./scripts/docker-local-llm-pull.sh
./scripts/docker-local-llm-web.sh
./scripts/docker-local-llm-create.sh
```

`README.md` and `.env.example` have also been updated with Dockerised local LLM and model-routing guidance.

### 2.6 Existing validation already performed

The current working tree has been validated with:

```text
uv run python -m pytest -q
91 passed, 1 warning

uv run ruff format --check .
76 files already formatted

uv run ruff check .
All checks passed

uv run mypy musicagent
Success: no issues found in 29 source files

docker compose --profile app --profile crews --profile agents --profile local-llm config
Rendered expected local-LLM entries

uv run musicagent create ...
Manual default stub-mode CLI smoke passed
```

## 3. Core architecture decisions

### 3.1 Docker is mandatory for local LLM runtime

The local LLM must run in Docker as part of the repository-managed Compose workflow.

Primary architecture:

```text
MusicAgent containers + Ollama container + OpenAI-compatible HTTP API
```

Host-managed Ollama is not the happy path. It may be mentioned only as a troubleshooting or experimentation fallback.

### 3.2 Ollama is the first runtime, not the only possible runtime

Ollama is a model-serving runtime, not a model. It runs model weights and exposes an HTTP API.

The actual models are things like:

- `llama3.1:8b`;
- `llama3.2:3b`;
- `mistral-nemo:12b`;
- `qwen2.5:14b`;
- `qwen2.5:32b`;
- `gemma2:9b`;
- `mixtral:8x7b`.

MusicAgent should remain coupled to the generic `openai-compatible` provider interface, not to Ollama-specific application code.

### 3.3 One model-server container can serve multiple models

The default design is one Dockerised model runtime with multiple pulled models in the same persistent model volume.

Do not start one container per model unless there is a measured performance or isolation need later.

### 3.4 Model routing order

Runtime routing must follow this order:

1. If `MUSICAGENT_USE_LOW_RESOURCE_MODEL=true` and `MUSICAGENT_LOW_RESOURCE_MODEL` is set, every agent uses the low-resource model.
2. Otherwise, if `MUSICAGENT_AGENT_MODEL_<AGENT_ID>` is set for the current agent, that model is used.
3. Otherwise, `MUSICAGENT_MODEL` is used.

### 3.5 Stub mode remains the default outside local-LLM flows

Default non-local-LLM workflows must remain:

```env
MUSICAGENT_LLM_PROVIDER=stub
```

This protects tests, CI, demos, and non-network local usage.

## 4. SOLID design requirements

All remaining implementation must explicitly follow SOLID principles.

### 4.1 Single Responsibility Principle

Each class/module should have one reason to change:

- configuration parsing belongs in `musicagent/config.py`;
- model routing belongs in `AgentModelRouter` or an equivalent routing abstraction;
- provider construction belongs in the LLM provider factory;
- agent execution belongs in `LLMAgentRunner`;
- Docker/runtime orchestration belongs in Compose and scripts, not Python business logic.

Do not mix model-routing rules into CLI command handlers, web handlers, MIDI generation, or task-output formatting.

### 4.2 Open/Closed Principle

The design must be open to adding new runtimes/models without modifying unrelated orchestration code.

Adding LocalAI, llama.cpp server, vLLM, or a hosted OpenAI-compatible endpoint should require configuration and provider-factory changes only, not changes to crew/task generation logic.

Adding a new model should require only:

- pulling the model into the runtime;
- setting an environment variable;
- optionally documenting the model.

### 4.3 Liskov Substitution Principle

Any object satisfying the LLM client protocol must be usable by `LLMAgentRunner`:

- `StubLLMClient`;
- OpenAI-compatible client;
- Azure OpenAI client;
- future LocalAI/llama.cpp/vLLM-compatible clients;
- test fakes.

Callers should not need provider-specific type checks.

### 4.4 Interface Segregation Principle

Agent orchestration should depend on the smallest useful interface:

```python
complete(agent_id: str, prompt: str, model: str | None = None) -> str
```

Do not force unrelated model-management operations such as pulling models, listing models, or health checks into the core completion interface. Those belong in separate diagnostics/runtime-management helpers.

### 4.5 Dependency Inversion Principle

High-level orchestration must depend on abstractions, not concrete provider implementations.

`CrewProjectGenerator` should depend on `AgentRunner`. `LLMAgentRunner` should depend on `LLMClient` and `AgentModelRouter`. CLI/web entrypoints should not instantiate `ChatOpenAI`, `AzureChatOpenAI`, or Ollama-specific clients directly.

## 5. Runtime alternatives

The current implementation starts with Dockerised Ollama. Other Docker-capable runtimes remain future options.

| Runtime | Docker suitability | Model formats/families | Strengths | Weaknesses | Current decision |
| --- | --- | --- | --- | --- | --- |
| Ollama | Excellent | Llama, Qwen, Mistral, Gemma, Phi, Mixtral, many GGUF-backed models | Simple, popular, OpenAI-compatible endpoint, easy model pulls, named volume persistence | Less tunable than vLLM/TGI for high-throughput serving | Implemented first |
| LocalAI | Good | GGUF, llama.cpp-compatible models, some multimodal/audio backends depending on setup | OpenAI-compatible, Docker-friendly, broad backend support, can serve more than text | More configuration complexity | Future option if backend flexibility is needed |
| llama.cpp server | Good | GGUF models | Lightweight, efficient CPU/GGUF serving, very controllable | More manual model-file management | Future CPU/control option |
| vLLM | Good on GPU workstations/servers | Hugging Face transformer models | High throughput, batching, production-like OpenAI-compatible server | GPU-focused and heavier | Future GPU/server option |
| Text Generation Inference | Good on GPU servers | Hugging Face transformer models | Production-grade serving | Heavy and overkill for local dev | Not first choice |
| LM Studio server | Weak for repo-managed Docker | Desktop-downloaded GGUF models | Good manual experimentation UX | Not Compose-first | Manual experimentation only |

## 6. Model recommendations

### 6.1 Recommended model set

Use this model order for the Dockerised local LLM stack:

```text
Repo-wide practical default: llama3.1:8b
Preferred quality upgrade: qwen2.5:14b
Low-resource fallback: llama3.2:3b
Creative/lyric option: mistral-nemo:12b
Concise/general alternative: gemma2:9b
High-quality workstation option: qwen2.5:32b
High-end experiment: llama3.1:70b
```

### 6.2 Initial routing recommendation

| Agent/work type | Suggested model | Why |
| --- | --- | --- |
| Default/general agents | `llama3.1:8b` | Best practical default across normal developer machines. |
| Lyricist/topliner | `mistral-nemo:12b` | Stronger creative prose, lyric phrasing, and alternate hook language. |
| Critic/reviewer | `qwen2.5:14b` | Better instruction-following and checklist-style critique. |
| MIDI/control/schema producer | `qwen2.5:14b` or `qwen2.5:32b` | Better structured-output reliability. |
| Low-resource mode | `llama3.2:3b` | Fast fallback when Docker memory is constrained. |

### 6.3 Why not default to a coding model

Do not default MusicAgent runtime crews to `qwen2.5-coder` or another coding-specialised model.

MusicAgent runtime output is music direction, lyric/topline ideas, arrangement critique, and structured creative metadata. Code models can be evaluated later for strict JSON/schema hand-offs, but a general instruct model is the better first runtime fit.

### 6.4 Hardware guidance

| Model size | Typical practical memory range | Expected MusicAgent experience |
| --- | --- | --- |
| 3B | 4-8 GB available RAM/VRAM | Fast smoke tests; weak creative depth. |
| 7B/8B/9B | 8-16 GB available RAM/VRAM | Best everyday developer experience. |
| 12B/14B | 16-32 GB available RAM/VRAM | Better quality; preferred if latency is acceptable. |
| 30B/32B | 32-64 GB available RAM/VRAM | High-quality workstation mode. |
| 70B | 64 GB+ available RAM/VRAM | Experimental only. |

Docker Desktop memory limits matter. If Docker is limited to 8 GB, use `llama3.2:3b` or `llama3.1:8b`. If Docker has 16-32 GB available, test `qwen2.5:14b` and `mistral-nemo:12b`.

## 7. Phase A-D implementation status

Phases A-D have now been implemented in the working tree. Future work should refine these capabilities rather than duplicating them.

### Phase A: Explicit diagnostics implemented

Implemented:

1. `musicagent config` prints non-secret settings diagnostics.
2. `musicagent llm-check` performs optional reachability and model checks.
3. Diagnostics report safe metadata only:
   - provider;
   - selected default model;
   - low-resource mode state;
   - per-agent model names;
   - whether a base URL is configured;
   - redacted base URL host only;
   - success/failure;
   - never API key values.
4. `./scripts/docker-local-llm-check.sh` runs diagnostics through the Dockerised local-LLM service.
5. `/api/config` exposes the same non-secret configuration metadata for the web API.

### Phase B: Model availability checks implemented

Implemented:

1. `check_model_availability(...)` safely checks configured models against OpenAI-compatible `/v1/models` inventory.
2. Ollama `/api/tags` is used as a fallback inventory endpoint when the configured base URL ends in `/v1`.
3. Checks include:
   - `MUSICAGENT_MODEL`;
   - `MUSICAGENT_LOW_RESOURCE_MODEL` when set;
   - all `MUSICAGENT_AGENT_MODEL_<AGENT_ID>` values.
4. Missing models are reported by name only.
5. Diagnostics suggest exact pull commands such as `./scripts/docker-local-llm-pull.sh mistral-nemo:12b`.

### Phase C: Structured-output hardening implemented

Implemented:

1. `AgentStructuredOutput` defines the initial Pydantic schema for agent hand-offs.
2. `StructuredAgentResponder` prompts non-stub LLM calls to return JSON only.
3. Malformed output is validated and repaired with one retry prompt.
4. JSON data files now use validated structured output as the machine-readable source.
5. Markdown output is derived from structured output, with raw response included only when validation fails.

Remaining refinement:

- Add richer task-specific schemas once each agent's final data contract is agreed.
- Run live model evaluation across `llama3.1:8b`, `mistral-nemo:12b`, and `qwen2.5:14b` after models are pulled locally.

### Phase D: Non-Ollama runtime evaluation path implemented

Implemented:

1. `musicagent llm-runtimes` exposes the current runtime evaluation order.
2. Runtime alternatives are represented as structured diagnostics data.
3. Ollama remains the implemented-first runtime.
4. LocalAI, llama.cpp server, and vLLM remain future options behind the same OpenAI-compatible architecture.

Triggers for deeper evaluation remain:

- Ollama cannot reliably serve the selected models in Docker;
- model-pull/runtime behaviour is too opaque;
- performance is inadequate on target hardware;
- we need backends Ollama does not support;
- we need GPU throughput better handled by vLLM.

## 8. Dockerised local LLM workflow

Pull the default model:

```bash
./scripts/docker-local-llm-pull.sh llama3.1:8b
```

Pull optional routed models:

```bash
./scripts/docker-local-llm-pull.sh mistral-nemo:12b
./scripts/docker-local-llm-pull.sh qwen2.5:14b
./scripts/docker-local-llm-pull.sh llama3.2:3b
```

Run the Dockerised local LLM web app:

```bash
./scripts/docker-local-llm-web.sh
```

Generate through the Dockerised local LLM stack:

```bash
./scripts/docker-local-llm-create.sh --name local-llm-example --prompt "dark electronic alt-pop with a huge chorus" --crew electronic_alt_pop --overwrite
```

## 9. Model evaluation prompt pack

Before changing the documented default from `llama3.1:8b`, test candidate models with the same MusicAgent-specific prompt pack:

1. Generate an electronic/alternative pop arrangement brief with sections, track roles, BPM, key, and production notes.
2. Generate a singer-songwriter acoustic arrangement with chords, vocal contour, accompaniment notes, and dynamic arc.
3. Produce strict JSON matching a Pydantic schema for one agent task.
4. Produce a critique pass that identifies weak hooks, arrangement clutter, and missing contrast.
5. Produce lyric/topline options for a chorus and explain melodic contour.
6. Repeat the same prompt three times and compare consistency.

Success criteria:

- follows the requested role;
- does not invent unsupported files or tools;
- returns parseable structured output when requested;
- gives musically useful, not generic, arrangement decisions;
- responds quickly enough across all tasks in a crew;
- keeps outputs distinct between agents.

## 10. Acceptance criteria for the completed local LLM capability

Local LLM support is complete when:

1. The repository can start a local LLM server in Docker through Compose.
2. MusicAgent containers can call the LLM container by service name, not host `localhost`.
3. A developer can generate a project through the Dockerised local LLM stack without a real OpenAI token.
4. CLI project generation invokes the configured local model when `MUSICAGENT_LLM_PROVIDER=openai-compatible`.
5. Web project generation uses the same provider selection path as the CLI.
6. Stub mode remains the default for non-local-LLM workflows and requires no credentials.
7. Missing configuration errors list only missing variable names, not values.
8. MusicAgent can route lyric/topline agents to `mistral-nemo:12b`, critic/reviewer agents to `qwen2.5:14b`, and default agents to `llama3.1:8b` from the same Dockerised runtime.
9. `MUSICAGENT_USE_LOW_RESOURCE_MODEL=true` routes every agent to `llama3.2:3b` when needed.
10. Tests cover provider wiring, per-agent routing, low-resource override, Compose config, scripts, and docs without live model calls.
11. Diagnostics can verify provider config and model-server reachability without leaking credentials.
12. No credentials are written to generated outputs, logs, docs, tests, or Compose files.

## 11. Final decisions

| Question | Decision |
| --- | --- |
| Where should the local LLM run? | In Docker, managed by this repo's Compose workflow. |
| Which runtime should be used first? | Ollama container exposing its OpenAI-compatible `/v1` API. |
| Is Ollama the model? | No. Ollama is the serving runtime; models are Llama, Qwen, Mistral, Gemma, etc. |
| Should host-managed Ollama be the default? | No. It can be a troubleshooting fallback only. |
| What should MusicAgent containers call? | `http://ollama:11434/v1`, not host `localhost`. |
| Should `openai-compatible` require `OPENAI_API_KEY` for local providers? | Yes for now. Use `ollama-local-placeholder`; do not inject silently. |
| Which model should `.env.example` default to? | `llama3.1:8b`, because it is practical for more machines. |
| Which model is the quality recommendation? | `qwen2.5:14b`, if Docker has enough memory. |
| Which model should lyric/topline agents use? | `mistral-nemo:12b`, when pulled and configured. |
| Which model should low-resource mode use? | `llama3.2:3b`. |
| Should code-specialised models be default runtime models? | No. General instruct models fit music-generation crews better. |
| Should per-agent model routing be part of the design? | Yes. Default, per-agent, and low-resource routing are part of the baseline design. |
| What design principles govern implementation? | SOLID: separate config, routing, provider construction, orchestration, and runtime management behind small abstractions. |
