"""Vercel entrypoint for the Chicago Stroll API."""

from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Chicago Stroll",
    version="0.1.0",
)

app.include_router(router)