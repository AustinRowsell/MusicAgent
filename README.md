# MusicAgent

MusicAgent is a Python-based multi-agent music creation tool for generating structured song assets, markdown briefs, JSON data, and per-track MIDI files. It supports both a Typer CLI and a local FastAPI web API using the same generation services.

## Requirements

- Python `>=3.14,<3.15`
- [`uv`](https://docs.astral.sh/uv/) for dependency and environment management
- Docker Desktop or a compatible Docker daemon only if you want container workflows

## Install

Bootstrap the local project environment:

```bash
./scripts/install.sh
```

This syncs the project `.venv`, makes helper scripts executable, and runs a CLI smoke check.

To also install `musicagent` as a user-level `uv` tool from this checkout:

```bash
./scripts/install.sh --user
```

To skip post-install checks:

```bash
./scripts/install.sh --skip-checks
```

## Local CLI

List built-in crews:

```bash
./scripts/local-cli.sh crews
```

Create an electronic project:

```bash
./scripts/local-cli.sh create --name electronic-example --prompt "bright indietronica with a hooky drop" --crew electronic_alt_pop --output outputs --dry-run --overwrite
```

Create an acoustic project:

```bash
./scripts/local-cli.sh create --name acoustic-example --prompt "intimate acoustic song" --crew acoustic --output outputs --dry-run --overwrite
```

## Local web API

Start the FastAPI app:

```bash
./scripts/local-web.sh
```

Then open:

```text
http://localhost:8000/
```

Check crews:

```bash
curl http://localhost:8000/api/crews
```

## Docker helper scripts

The Docker helpers wrap the required Compose profiles so you do not need to remember the full commands.

List crews in the app profile:

```bash
./scripts/docker-cli.sh crews
```

Create a project in the app profile; generated files are written to host `outputs/` through the `./outputs:/app/outputs` bind mount:

```bash
./scripts/docker-create.sh --name electronic-example --prompt "bright indietronica" --crew electronic_alt_pop --dry-run --overwrite
```

Start the web service:

```bash
./scripts/docker-web.sh
```

Run crew profile placeholders:

```bash
./scripts/docker-crew.sh electronic
./scripts/docker-crew.sh acoustic
```

Run agent profile placeholders:

```bash
./scripts/docker-agent.sh groove
./scripts/docker-agent.sh sound
./scripts/docker-agent.sh critic
./scripts/docker-agent.sh lyricist
./scripts/docker-agent.sh topliner
./scripts/docker-agent.sh harmony
```

## Outputs

Generated projects are written under `outputs/` by default. A project contains markdown files, JSON data, `session_manifest.json`, and per-track MIDI files such as:

```text
midi/drums.mid
midi/bass.mid
midi/chords.mid
midi/hooks.mid
midi/vocal_melody.mid
midi/accompaniment.mid
```

`full_sketch.mid` is not required or generated as the primary deliverable. Per-track/per-instrument MIDI files are the main output model.

## Configuration and credentials

Use `.env.example` for documented local configuration names. Copy it to `.env` only for local use when needed.

Never commit real .env files or credential values. Do not put real API keys in Compose files, documentation, manifests, generated outputs, or tests.

Default offline mode uses the deterministic stub provider:

```text
MUSICAGENT_LLM_PROVIDER=stub
```

Non-stub providers are configured through environment variables and validated without printing credential values.

## Dockerised local LLM

The local LLM runs as a Docker Compose service. Ollama is the first supported container runtime, but Ollama is not the model: it can serve models such as `llama3.1:8b`, `llama3.2:3b`, `mistral-nemo:12b`, and `qwen2.5:14b`.

Pull the broad-compatibility default model into the Docker volume:

```bash
./scripts/docker-local-llm-pull.sh llama3.1:8b
```

Pull optional routed models when you want stronger lyric/critic behaviour:

```bash
./scripts/docker-local-llm-pull.sh mistral-nemo:12b
./scripts/docker-local-llm-pull.sh qwen2.5:14b
```

Run the web app against the Dockerised local LLM:

```bash
./scripts/docker-local-llm-web.sh
```

Run CLI commands against the Dockerised local LLM:

```bash
./scripts/docker-local-llm-create.sh --name local-llm-example --prompt "dark electronic alt-pop with a huge chorus" --crew electronic_alt_pop --overwrite
```

Inspect non-secret local LLM configuration and runtime status:

```bash
./scripts/local-cli.sh config
./scripts/local-cli.sh llm-runtimes
./scripts/docker-local-llm-check.sh
```

`llm-check` reports provider, configured models, model availability, and reachability without printing API key values. If a configured model is missing from the Dockerised runtime, it suggests the exact `./scripts/docker-local-llm-pull.sh <model>` command to run.

For ready-made workstation profiles from minimum hardware to high-end home setups, see `.env.local-llm-profiles.example`.

For a complete real-runtime Docker walkthrough that creates a `singer_songwriter_acoustic` song with Ollama-served models, see [`docs/singer-songwriter-acoustic-e2e.md`](docs/singer-songwriter-acoustic-e2e.md).

The local-LLM profile defaults to one Ollama container with multiple models available in the same `ollama-models` volume:

```text
MUSICAGENT_MODEL=llama3.1:8b
MUSICAGENT_OPENAI_BASE_URL=http://ollama:11434/v1
MUSICAGENT_AGENT_MODEL_LYRICIST_POET=mistral-nemo:12b
MUSICAGENT_AGENT_MODEL_TOPLINER=mistral-nemo:12b
MUSICAGENT_AGENT_MODEL_CYBER_CRITIC=qwen2.5:14b
MUSICAGENT_LOW_RESOURCE_MODEL=llama3.2:3b
```

Set `MUSICAGENT_USE_LOW_RESOURCE_MODEL=true` to route every agent to `llama3.2:3b` temporarily, even when per-agent overrides are configured.

`OPENAI_API_KEY=ollama-local-placeholder` is used only as a local placeholder for Ollama's OpenAI-compatible API. It is not a real OpenAI credential.

## Validation

Run the standard checks:

```bash
uv run python -m pytest -q
uv run ruff format --check .
uv run ruff check .
uv run mypy musicagent
```

Validate Compose configuration without starting containers:

```bash
docker compose --profile app --profile crews --profile agents config
```

## More detail

See `docs/planning/containerisation-decisions.md` for the full containerisation decisions, Compose profiles, helper script explanations, and troubleshooting notes.
