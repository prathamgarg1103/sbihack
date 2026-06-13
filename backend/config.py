"""Central configuration for the Saarthi backend.

Only ANTHROPIC_API_KEY is strictly required (see CLAUDE.md / .env.example).
Everything else has a safe local default.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the repo root (one level above /backend).
BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
load_dotenv(REPO_ROOT / ".env")

# --- Secrets ---
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")

# --- Agent ---
# Per CLAUDE.md the agent reasoning core runs on claude-sonnet-4-6.
MODEL: str = os.getenv("SAARTHI_MODEL", "claude-sonnet-4-6")
MAX_TOKENS: int = int(os.getenv("SAARTHI_MAX_TOKENS", "2048"))

# --- Paths ---
DATA_DIR = BACKEND_DIR / "data"
CORPUS_DIR = DATA_DIR / "corpus"
TRANSACTIONS_PATH = DATA_DIR / "transactions.json"
FEEDBACK_DB = BACKEND_DIR / "feedback.db"

# --- CORS (Vite dev server) ---
FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def has_api_key() -> bool:
    return bool(ANTHROPIC_API_KEY and ANTHROPIC_API_KEY.strip())
