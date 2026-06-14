"""Vercel serverless entry point.

Mounts the existing FastAPI backend under /api so that production requests
(`/api/health`, `/api/personas/...`) reach the same routes the local dev server
serves at `/health`, `/personas/...` (where the Vite proxy strips `/api`).
"""
import sys
from pathlib import Path

# Make the backend package importable (bundled via vercel.json includeFiles).
BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from fastapi import FastAPI  # noqa: E402
from main import app as backend_app  # noqa: E402

app = FastAPI()
app.mount("/api", backend_app)
