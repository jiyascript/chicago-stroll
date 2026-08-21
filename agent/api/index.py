"""Minimal Vercel diagnostic entrypoint."""

from fastapi import FastAPI


app = FastAPI(
    title="Chicago Stroll",
    version="0.1.0",
)


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok"
    }