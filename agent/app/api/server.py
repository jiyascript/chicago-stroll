from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.api.routes import router
app=FastAPI(title="Chicago Stroll",version="2.0.0"); app.include_router(router)
PUBLIC=Path(__file__).resolve().parents[2]/"public"
@app.get("/",include_in_schema=False)
def home(): return FileResponse(PUBLIC/"index.html")
@app.get("/app.js",include_in_schema=False)
def js(): return FileResponse(PUBLIC/"app.js")
@app.get("/styles.css",include_in_schema=False)
def css(): return FileResponse(PUBLIC/"styles.css")
