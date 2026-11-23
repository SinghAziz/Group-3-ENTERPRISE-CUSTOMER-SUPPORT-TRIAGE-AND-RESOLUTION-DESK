from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # Dependencies are optional for the credential-free Python workflow.
    def load_dotenv() -> None:
        return None

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("RELAYIT_DB_PATH", str(ROOT_DIR / "relayit.db")))
CONFIDENCE_THRESHOLD = float(os.getenv("RELAYIT_CONFIDENCE_THRESHOLD", "0.62"))
MODEL_PROVIDER = os.getenv("RELAYIT_MODEL_PROVIDER", "deterministic").lower()
TECHNICAL_DOCS_DIR = ROOT_DIR / "relayit" / "knowledge_base" / "technical"
