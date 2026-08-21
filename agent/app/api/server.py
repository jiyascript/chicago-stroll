from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import router

app = FastAPI(title = "Chicago Stroll", version = "0.1.0")
app.include_router(router)

WEB_DIR = Path(__file__).resolve().parents[2] / "public"

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
@app.get("/styles.css", include_in_schema=False)
def styles() -> FileResponse:
    return FileResponse(
        WEB_DIR / "styles.css"
    )


@app.get("/app.js", include_in_schema=False)
def javascript() -> FileResponse:
    return FileResponse(
        WEB_DIR / "app.js"
    )
@app.get("/", include_in_schema=False)
def web_app() -> FileResponse:
    """Serve the Chicago Stroll web experience."""
    return FileResponse(WEB_DIR / "index.html")
