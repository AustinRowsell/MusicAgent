# Containerisation Decisions and Operator Workflows

This document records the container runtime decisions implemented from the phase 7 roadmap and gives copy-pasteable local workflows for operators. CLI and web are both first-class interfaces and call shared MusicAgent service-layer code. Crew and agent containers are deployment profiles, not separate code forks.

## Installer

Run the installer once after cloning the repository to sync the local environment, make helper scripts executable, and run a CLI smoke check:

```bash
./scripts/install.sh
```

The default install is local to this checkout and uses `uv run musicagent crews` for validation. To also expose `musicagent` as a user-level `uv` tool from this checkout, run:

```bash
./scripts/install.sh --user
```

Use `./scripts/install.sh --skip-checks` when dependencies are already synced and you only want the bootstrap steps.

## Helper scripts

The `scripts/` directory contains shortcuts for the common local and Docker workflows so operators do not need to remember full Docker Compose profile commands.

```bash
./scripts/local-cli.sh crews
./scripts/local-web.sh
./scripts/docker-cli.sh crews
./scripts/docker-create.sh --name electronic-example --prompt "bright indietronica with a hooky drop" --crew electronic_alt_pop --dry-run --overwrite
./scripts/docker-web.sh
./scripts/docker-crew.sh electronic
./scripts/docker-agent.sh groove
```

## Local CLI run

List built-in crews without Docker:

```bash
./scripts/local-cli.sh crews
```

Equivalent raw command:

```bash
uv run musicagent crews
```

Create an electronic project locally:

```bash
uv run musicagent create --name electronic-example --prompt "bright indietronica with a hooky drop" --crew electronic_alt_pop --output outputs --dry-run --overwrite
```

Create an acoustic project locally:

```bash
uv run musicagent create --name acoustic-example --prompt "intimate acoustic song with a reflective chorus" --crew singer_songwriter_acoustic --output outputs --dry-run --overwrite
```

Expected per-track MIDI examples include `midi/drums.mid`, `midi/bass.mid`, `midi/chords.mid`, `midi/hooks.mid`, `midi/vocal_melody.mid`, and `midi/accompaniment.mid`. A single combined MIDI file is not the main deliverable.

## Local web run

Start the FastAPI app without Docker:

```bash
./scripts/local-web.sh
```

Equivalent raw command:

```bash
uv run uvicorn musicagent.web.app:app --host 127.0.0.1 --port 8000
```

Open the dashboard at <http://localhost:8000/> or check crew data:

```bash
curl http://localhost:8000/api/crews
```

Download a generated MIDI asset after creating a project:

```bash
curl -o drums.mid "http://localhost:8000/api/projects/electronic-example/midi/drums.mid?output_root=outputs"
```

## Compose app profile

The `app` profile is the simplest local container mode. It provides the one-off CLI service and local web API.

```bash
./scripts/docker-cli.sh crews
```

Equivalent raw command:

```bash
docker compose --profile app run --rm musicagent-cli crews
```

Create an electronic project through the CLI container and write outputs to the host `./outputs` directory:

```bash
./scripts/docker-create.sh --name electronic-example --prompt "bright indietronica with a hooky drop" --crew electronic_alt_pop --dry-run --overwrite
```

Equivalent raw command:

```bash
docker compose --profile app run --rm musicagent-cli create --name electronic-example --prompt "bright indietronica with a hooky drop" --crew electronic_alt_pop --output /app/outputs --dry-run --overwrite
```

Start the web API container:

```bash
./scripts/docker-web.sh
```

Equivalent raw command:

```bash
docker compose --profile app up musicagent-web
```

Then verify the API:

```bash
curl http://localhost:8000/api/crews
```

## Compose crew profile

The `crews` profile runs the web API plus one lightweight worker service per built-in crew. Each service uses the same image and shared code path while setting `MUSICAGENT_CREW_ID` for deployment-specific configuration.

```bash
./scripts/docker-crew.sh electronic
```

Equivalent raw command:

```bash
docker compose --profile crews run --rm electronic-alt-pop-crew
```

```bash
./scripts/docker-crew.sh acoustic
```

Equivalent raw command:

```bash
docker compose --profile crews run --rm singer-songwriter-acoustic-crew
```

Crew-specific smoke generation can still use the shared CLI command:

```bash
docker compose --profile app run --rm musicagent-cli create --name electronic-crew-smoke --prompt "crew profile electronic smoke" --crew electronic_alt_pop --output /app/outputs --dry-run --overwrite
```

```bash
docker compose --profile app run --rm musicagent-cli create --name acoustic-crew-smoke --prompt "crew profile acoustic smoke" --crew singer_songwriter_acoustic --output /app/outputs --dry-run --overwrite
```

## Compose agent profile

The `agents` profile runs the web API plus one lightweight worker service per initial built-in agent. Agent services are deployment profiles, not separate code forks. They preserve the same `AgentRunner`, prompt, registry, and structured output contracts as the app and crew profiles.

```bash
./scripts/docker-agent.sh groove
```

Equivalent raw command:

```bash
docker compose --profile agents run --rm groove-architect-agent
```

```bash
./scripts/docker-agent.sh sound
```

Equivalent raw command:

```bash
docker compose --profile agents run --rm sound-designer-agent
```

```bash
./scripts/docker-agent.sh critic
```

Equivalent raw command:

```bash
docker compose --profile agents run --rm cyber-critic-agent
```

```bash
./scripts/docker-agent.sh lyricist
```

Equivalent raw command:

```bash
docker compose --profile agents run --rm lyricist-poet-agent
```

```bash
./scripts/docker-agent.sh topliner
```

Equivalent raw command:

```bash
docker compose --profile agents run --rm topliner-agent
```

```bash
./scripts/docker-agent.sh harmony
```

Equivalent raw command:

```bash
docker compose --profile agents run --rm harmonic-accompanist-agent
```

## Output mounts

Compose bind mounts `./outputs:/app/outputs` so generated assets appear on the host. When `./inputs` exists, it is mounted read-only as `./inputs:/app/inputs:ro` so reference material can be used without copying it into the image.

Generated project folders contain markdown, JSON data, a `session_manifest.json`, and per-track MIDI files. Do not commit generated `outputs/` artifacts unless a specific review requires fixture data.

## Environment configuration

Use `.env.example` as the list of documented local configuration names. Copy it to `.env` for local-only configuration when using real providers. The real `.env` file is ignored and must not be committed.

Default offline mode uses:

```text
MUSICAGENT_LLM_PROVIDER=stub
```

Non-stub providers require their documented environment variable names to be populated locally. Never put real credential values in Compose files, manifests, documentation, generated outputs, or commits.

## Batch manifest example

If a batch manifest workflow is used, keep input paths under the mounted `/app/inputs` tree and output roots under `/app/outputs`. Example command shape:

```bash
docker compose --profile app run --rm musicagent-cli batch --manifest /app/inputs/batch-manifest.json --output /app/outputs
```

If the batch command is not enabled in a local checkout, use repeated `musicagent create` commands with the same mounted input and output directories.

## Troubleshooting

- If Docker commands fail with a missing Docker socket, start Docker Desktop or the local Docker daemon and retry.
- If `docker compose --profile app config` reports a missing `.env`, upgrade Docker Compose or use the committed optional `env_file` syntax in `compose.yaml`.
- If generated files do not appear on the host, confirm the command uses `--output /app/outputs` inside the container.
- If an input file is not visible in a container, place it under host `./inputs` and refer to it via `/app/inputs/...`.
- If a non-stub provider fails at startup, check that the required environment variable names are present in local `.env`; do not print credential values while debugging.
