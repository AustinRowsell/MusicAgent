# End-to-End Singer-Songwriter Acoustic Song Workflow

This guide walks through creating a real `singer_songwriter_acoustic` song project with MusicAgent using Docker, Ollama, and an actual local model. It avoids the deterministic stub provider so the generated song assets come from a real LLM runtime.

## Goal

Create a complete acoustic song sketch with:

- a project brief;
- lyrics;
- topline direction;
- acoustic accompaniment direction;
- structured JSON data for each agent step;
- per-track MIDI files for `vocal_melody` and `accompaniment`;
- a session manifest recording the generated assets.

The shortest real-runtime path is:

```text
Docker Compose -> Ollama container -> llama3.2:3b model -> MusicAgent CLI container -> outputs/<song-name>/
```

## Why this workflow uses Docker

Docker keeps the application runtime, LLM server, and model storage reproducible:

- MusicAgent runs in a Python container built from this repository.
- Ollama runs in a separate container and exposes an OpenAI-compatible API.
- Model files are stored in the persistent Docker volume `ollama-models`.
- Generated song files are bind-mounted back to the host under `./outputs`.

This means the application container never needs a real hosted OpenAI key for local work. The `OPENAI_API_KEY=ollama-local-placeholder` value used below is only a non-secret placeholder required by the OpenAI-compatible client interface when talking to local Ollama.

## Prerequisites

Install and start:

- Docker Desktop, or another Docker daemon with Docker Compose support;
- enough disk space for the selected model;
- this repository checked out locally.

For the smallest practical real-LLM setup, allocate roughly 4-8 GB of memory to Docker and use `llama3.2:3b`. Larger models can improve quality, but they are not required for this minimal end-to-end path.

## Step 1: Confirm the acoustic crew exists

Run the CLI container through the app profile:

```bash
./scripts/docker-cli.sh crews
```

Why: this verifies that Docker can build/run the MusicAgent image and that the built-in crew registry is available inside the container.

Expected output includes:

```text
singer_songwriter_acoustic: Singer-Songwriter / Acoustic Crew [...]
```

## Step 2: Use the minimal real local-LLM configuration

Create a local `.env` file for this repository only:

```bash
cat > .env <<'EOF'
MUSICAGENT_INPUT_MODE=copy
MUSICAGENT_LLM_PROVIDER=openai-compatible
MUSICAGENT_DEPLOYMENT_PROFILE=app
MUSICAGENT_OUTPUT_ROOT=outputs
MUSICAGENT_MODEL=llama3.2:3b
MUSICAGENT_OPENAI_BASE_URL=http://ollama:11434/v1
OPENAI_API_KEY=ollama-local-placeholder
MUSICAGENT_LOW_RESOURCE_MODEL=llama3.2:3b
MUSICAGENT_USE_LOW_RESOURCE_MODEL=true
EOF
```

Why each setting matters:

| Setting | Purpose |
| --- | --- |
| `MUSICAGENT_LLM_PROVIDER=openai-compatible` | Forces MusicAgent to use a real OpenAI-compatible LLM endpoint instead of stub mode. |
| `MUSICAGENT_MODEL=llama3.2:3b` | Selects the smallest practical Ollama-served model for the workflow. |
| `MUSICAGENT_OPENAI_BASE_URL=http://ollama:11434/v1` | Points MusicAgent containers at the Ollama service name inside Compose networking. |
| `OPENAI_API_KEY=ollama-local-placeholder` | Satisfies client configuration locally; it is not a real credential. |
| `MUSICAGENT_USE_LOW_RESOURCE_MODEL=true` | Routes every agent to `llama3.2:3b` for the minimum setup. |
| `MUSICAGENT_OUTPUT_ROOT=outputs` | Documents the host-side output root; Docker commands still write to `/app/outputs` inside the container. |

Do not commit `.env`. It is intentionally ignored and may contain local-only settings.

## Step 3: Pull the actual model into Docker

Pull the model into the `ollama-models` Docker volume:

```bash
./scripts/docker-local-llm-pull.sh llama3.2:3b
```

Why: the MusicAgent container calls Ollama at generation time, but Ollama must have the model weights available first. This command starts the Compose local-LLM profile if needed and runs `ollama pull llama3.2:3b` against the Dockerised Ollama service.

There are two separate certificate paths in this Docker workflow:

1. The MusicAgent image build downloads Python dependencies from PyPI with `uv`. If `./certs` contains `.crt` or `.pem` files, the Docker helper scripts concatenate them into the ignored local bundle `./certs/musicagent-local-ca-bundle.pem`, enable `compose.local-certs.yaml`, and pass that bundle into the build as a Docker BuildKit secret. The Dockerfile installs the secret into the container trust store before running `uv pip install --system --system-certs .`.
2. The Ollama container downloads model weights from `registry.ollama.ai`. The same `compose.local-certs.yaml` override mounts `./certs` read-only into the Ollama container and extends `SSL_CERT_DIR` for that runtime model pull. If `./certs` is absent or contains no certificate files, the default Compose configuration is used with no certificate mount or build secret.

Do not commit local certificate files. The `certs/` directory is intentionally ignored by Git and excluded from normal Docker build contexts. The generated `musicagent-local-ca-bundle.pem` is a local BuildKit secret input, not an application asset.

This can take time on the first run because model weights are downloaded. Later runs reuse the persistent `ollama-models` volume.

## Step 4: Check runtime and model availability

Run the non-secret LLM diagnostic:

```bash
./scripts/docker-local-llm-check.sh
```

Why: this confirms three things before generating a song:

1. MusicAgent is using `openai-compatible`, not `stub`.
2. MusicAgent can reach Ollama through `http://ollama:11434/v1`.
3. The configured model `llama3.2:3b` is available in the Ollama runtime.

A healthy minimal result should report:

```text
provider: openai-compatible
configured model: llama3.2:3b
missing models: []
reachability ok: true
model availability ok: true
```

If the check reports a missing model, run the exact pull command suggested by the diagnostic and repeat this step.

## Step 5: Generate the acoustic song project

Run the real local-LLM create command:

```bash
./scripts/docker-local-llm-create.sh --name singer-songwriter-acoustic-example --prompt "Write an intimate singer-songwriter acoustic song about leaving a city at dawn, with honest verses, a memorable chorus, fingerpicked guitar, and a restrained hopeful ending." --crew singer_songwriter_acoustic --tempo 84 --key "G major" --overwrite
```

Why these parameters are used:

- `--crew singer_songwriter_acoustic` selects the acoustic workflow rather than the electronic crew.
- `--tempo 84` puts the song in a natural acoustic ballad range.
- `--key "G major"` gives the harmonic/accompaniment agent a guitar-friendly tonal centre.
- `--overwrite` makes the example repeatable while you iterate.
- No `--dry-run` flag is used because this guide is for a real model-backed generation path.

The command writes files to `/app/outputs` inside the container, which is bind-mounted to `./outputs` on the host.

## Step 6: Inspect the generated files

Open the generated project directory:

```bash
ls -R outputs/singer-songwriter-acoustic-example
```

Expected shape:

```text
outputs/singer-songwriter-acoustic-example/
  brief.md
  lyrics.md
  topline.md
  accompaniment.md
  session_manifest.json
  data/
    lyrics.json
    topline.json
    accompaniment.json
  midi/
    vocal_melody.mid
    accompaniment.mid
```

Why these files matter:

- `brief.md` captures the user prompt, selected crew, tempo, key, input mode, and requested song context.
- `lyrics.md` is the lyricist output for the acoustic song concept.
- `topline.md` describes melody/hook decisions for the vocal line.
- `accompaniment.md` describes harmonic and performance choices for guitar-first accompaniment.
- `data/*.json` provides structured data versions of the agent outputs for downstream automation.
- `midi/vocal_melody.mid` and `midi/accompaniment.mid` are the DAW-importable musical sketch files.
- `session_manifest.json` records the assets produced in the run.

## Step 7: Review the song assets

Read the creative outputs first:

```bash
sed -n '1,200p' outputs/singer-songwriter-acoustic-example/brief.md
sed -n '1,200p' outputs/singer-songwriter-acoustic-example/lyrics.md
sed -n '1,200p' outputs/singer-songwriter-acoustic-example/topline.md
sed -n '1,200p' outputs/singer-songwriter-acoustic-example/accompaniment.md
```

Why: the markdown files are the fastest way to decide whether the song concept, lyrical angle, vocal contour, and accompaniment plan are coherent before importing MIDI into a DAW.

Then check the manifest:

```bash
python -m json.tool outputs/singer-songwriter-acoustic-example/session_manifest.json
```

Why: the manifest confirms which files were generated and is the handoff point for any later automation.

## Step 8: Import the MIDI into a DAW

Import these files into your DAW or notation tool:

```text
outputs/singer-songwriter-acoustic-example/midi/vocal_melody.mid
outputs/singer-songwriter-acoustic-example/midi/accompaniment.mid
```

Suggested track setup:

| MIDI file | Suggested instrument | Role |
| --- | --- | --- |
| `vocal_melody.mid` | simple piano, vocal synth, or guide vocal instrument | Audition the topline contour. |
| `accompaniment.mid` | steel-string acoustic guitar or soft piano | Audition the harmonic bed. |

Why: MusicAgent exports per-track MIDI as the primary deliverable. It does not rely on a single combined `full_sketch.mid` file.

## Step 9: Iterate with a tighter prompt

If the result is too generic, keep the same setup and rerun with a more specific prompt:

```bash
./scripts/docker-local-llm-create.sh --name singer-songwriter-acoustic-example --prompt "Revise the acoustic song so verse one uses concrete dawn city images, the chorus title is 'Last Train Light', the vocal melody stays mostly stepwise, and the guitar part uses a gentle G-D-Em-C fingerpicking feel." --crew singer_songwriter_acoustic --tempo 84 --key "G major" --overwrite
```

Why: local models respond better when the requested imagery, title, melody shape, and accompaniment feel are explicit.

## Optional: Better acoustic songwriting model routing

The minimal setup routes every agent to `llama3.2:3b`. For stronger creative output on a machine with more memory, use a songwriter-oriented profile:

```bash
cat > .env <<'EOF'
MUSICAGENT_INPUT_MODE=copy
MUSICAGENT_LLM_PROVIDER=openai-compatible
MUSICAGENT_DEPLOYMENT_PROFILE=app
MUSICAGENT_OUTPUT_ROOT=outputs
MUSICAGENT_MODEL=llama3.1:8b
MUSICAGENT_OPENAI_BASE_URL=http://ollama:11434/v1
OPENAI_API_KEY=ollama-local-placeholder
MUSICAGENT_LOW_RESOURCE_MODEL=llama3.2:3b
MUSICAGENT_USE_LOW_RESOURCE_MODEL=false
MUSICAGENT_AGENT_MODEL_LYRICIST_POET=mistral-nemo:12b
MUSICAGENT_AGENT_MODEL_TOPLINER=mistral-nemo:12b
MUSICAGENT_AGENT_MODEL_HARMONIC_ACCOMPANIST=llama3.1:8b
EOF
```

Pull the referenced models:

```bash
./scripts/docker-local-llm-pull.sh llama3.1:8b
./scripts/docker-local-llm-pull.sh mistral-nemo:12b
./scripts/docker-local-llm-pull.sh llama3.2:3b
```

Then run:

```bash
./scripts/docker-local-llm-check.sh
./scripts/docker-local-llm-create.sh --name singer-songwriter-acoustic-example --prompt "Write an intimate singer-songwriter acoustic song about leaving a city at dawn, with honest verses, a memorable chorus, fingerpicked guitar, and a restrained hopeful ending." --crew singer_songwriter_acoustic --tempo 84 --key "G major" --overwrite
```

Why: `mistral-nemo:12b` is routed to lyric and topline work, while `llama3.1:8b` handles general and accompaniment work. The low-resource model remains available as a fallback switch.

## Optional: Run the local web API against the same real runtime

Start the Dockerised web service with Ollama:

```bash
./scripts/docker-local-llm-web.sh
```

Then verify the API from the host:

```bash
curl http://localhost:8000/api/crews
curl http://localhost:8000/api/config
```

Why: the CLI and web API use the same generation services, so this proves the real local runtime is available to both interfaces.

## Troubleshooting

### Docker cannot reach the model runtime

Run:

```bash
./scripts/docker-local-llm-check.sh
```

If reachability fails, make sure Docker is running and restart the local-LLM services:

```bash
docker compose --profile local-llm up -d ollama
./scripts/docker-local-llm-check.sh
```

### The model is missing

Pull the configured model:

```bash
./scripts/docker-local-llm-pull.sh llama3.2:3b
```

Then repeat:

```bash
./scripts/docker-local-llm-check.sh
```

### The machine is too slow or runs out of memory

Use the minimum profile from this guide:

```text
MUSICAGENT_MODEL=llama3.2:3b
MUSICAGENT_LOW_RESOURCE_MODEL=llama3.2:3b
MUSICAGENT_USE_LOW_RESOURCE_MODEL=true
```

Avoid larger models until the minimal workflow succeeds.

### The output still looks deterministic or generic

Check that `.env` does not contain:

```text
MUSICAGENT_LLM_PROVIDER=stub
```

Then rerun:

```bash
./scripts/docker-local-llm-check.sh
```

The provider should be `openai-compatible` for this guide.

## Clean up

Stop running containers without deleting downloaded models:

```bash
docker compose --profile local-llm down
```

Delete the generated example project if you no longer need it:

```bash
rm -rf outputs/singer-songwriter-acoustic-example
```

Only remove the model volume if you intentionally want to delete downloaded Ollama models:

```bash
docker volume rm musicagent_ollama-models
```

## Quick command summary

```bash
./scripts/docker-cli.sh crews
cat > .env <<'EOF'
MUSICAGENT_INPUT_MODE=copy
MUSICAGENT_LLM_PROVIDER=openai-compatible
MUSICAGENT_DEPLOYMENT_PROFILE=app
MUSICAGENT_OUTPUT_ROOT=outputs
MUSICAGENT_MODEL=llama3.2:3b
MUSICAGENT_OPENAI_BASE_URL=http://ollama:11434/v1
OPENAI_API_KEY=ollama-local-placeholder
MUSICAGENT_LOW_RESOURCE_MODEL=llama3.2:3b
MUSICAGENT_USE_LOW_RESOURCE_MODEL=true
EOF
./scripts/docker-local-llm-pull.sh llama3.2:3b
./scripts/docker-local-llm-check.sh
./scripts/docker-local-llm-create.sh --name singer-songwriter-acoustic-example --prompt "Write an intimate singer-songwriter acoustic song about leaving a city at dawn, with honest verses, a memorable chorus, fingerpicked guitar, and a restrained hopeful ending." --crew singer_songwriter_acoustic --tempo 84 --key "G major" --overwrite
ls -R outputs/singer-songwriter-acoustic-example
```
