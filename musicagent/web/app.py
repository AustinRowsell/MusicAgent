"""Local FastAPI web interface for MusicAgent."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, ConfigDict

from musicagent.io.outputs import slugify
from musicagent.models import ProjectRequest
from musicagent.orchestration.crew import CrewProjectGenerator
from musicagent.registries.crews import BuiltInCrewRegistry


class WebProjectRequest(BaseModel):
    """Request body for creating a project from the local web API."""

    model_config = ConfigDict(frozen=True)

    name: str
    prompt: str
    output_root: str
    crew: str = "electronic_alt_pop"
    tempo_bpm: int = 120
    key: str = "C major"
    dry_run: bool = True
    overwrite: bool = False
    review_pass: bool = False


def create_app() -> FastAPI:
    """Create the local web application."""

    app = FastAPI(title="MusicAgent")

    @app.get("/", response_class=HTMLResponse)
    def home() -> str:
        return """
        <!doctype html>
        <html>
          <head><title>MusicAgent</title></head>
          <body>
            <main>
              <h1>MusicAgent</h1>
              <p>Local project dashboard for generated crews, assets, and MIDI downloads.</p>
            </main>
          </body>
        </html>
        """

    @app.get("/api/crews")
    def crews() -> dict[str, list[dict[str, object]]]:
        registry = BuiltInCrewRegistry.default()
        return {
            "crews": [
                {
                    "id": crew.id,
                    "display_name": crew.display_name,
                    "aliases": list(crew.style_aliases),
                    "required_agents": list(crew.required_agents),
                }
                for crew in registry.list()
            ]
        }

    @app.post("/api/projects")
    def create_project(request: WebProjectRequest) -> dict[str, object]:
        project_request = ProjectRequest(
            name=request.name,
            prompt=request.prompt,
            output_root=Path(request.output_root),
            crew=request.crew,
            tempo_bpm=request.tempo_bpm,
            key=request.key,
            dry_run=request.dry_run,
            overwrite=request.overwrite,
            review_pass=request.review_pass,
        )
        result = CrewProjectGenerator().generate(project_request)
        return {
            "crew": result.crew.id,
            "project_root": str(result.project.root),
            "assets": [str(asset.path.relative_to(result.project.root)) for asset in result.assets],
        }

    @app.get("/api/projects/{project_id}/assets")
    def list_assets(
        project_id: str,
        output_root: str = Query(default="outputs"),
    ) -> dict[str, list[dict[str, str]]]:
        project_root = Path(output_root).expanduser() / project_id
        if not project_root.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        assets = [
            {"path": str(path.relative_to(project_root)), "name": path.name}
            for path in sorted(project_root.rglob("*"))
            if path.is_file()
        ]
        return {"assets": assets}

    @app.get("/api/projects/{project_id}/midi/{filename}")
    def download_midi(
        project_id: str,
        filename: str,
        output_root: str = Query(default="outputs"),
    ) -> FileResponse:
        project_root = Path(output_root).expanduser() / slugify(project_id)
        midi_path = project_root / "midi" / filename
        if not midi_path.exists() or midi_path.suffix.lower() not in {".mid", ".midi"}:
            raise HTTPException(status_code=404, detail="MIDI asset not found")
        return FileResponse(midi_path, media_type="audio/midi", filename=filename)

    return app


app = create_app()
