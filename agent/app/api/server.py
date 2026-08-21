from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import router

app = FastAPI(title = "Chicago Stroll", version = "0.1.0")
app.include_router(router)

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/", include_in_schema=False)
def web_app() -> FileResponse:
    """Serve the Chicago Stroll web experience."""
    return FileResponse(WEB_DIR / "index.html")
