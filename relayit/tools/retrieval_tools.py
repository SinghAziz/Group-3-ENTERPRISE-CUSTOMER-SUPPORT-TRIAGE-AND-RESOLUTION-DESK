from __future__ import annotations

import re
from pathlib import Path

from relayit.config import TECHNICAL_DOCS_DIR


def _chunks(text: str, size: int = 700) -> list[str]:
    return [text[index:index + size].strip() for index in range(0, len(text), size) if text[index:index + size].strip()]


def search_knowledge_base(query: str, docs_dir: Path = TECHNICAL_DOCS_DIR) -> list[dict[str, object]]:
    terms = set(re.findall(r"[a-z0-9]+", query.lower()))
    results: list[dict[str, object]] = []
    for path in sorted(docs_dir.glob("*.md")):
        for index, chunk in enumerate(_chunks(path.read_text(encoding="utf-8")), start=1):
            words = set(re.findall(r"[a-z0-9]+", chunk.lower()))
            score = len(terms & words) / max(len(terms), 1)
            if score:
                results.append({"source": path.name, "chunk": index, "score": round(score, 3), "content": chunk})
    return sorted(results, key=lambda item: float(item["score"]), reverse=True)[:3]


def evaluate_relevance(results: list[dict[str, object]], minimum: float = 0.08) -> dict[str, object]:
    relevant = [result for result in results if float(result["score"]) >= minimum]
    return {"relevant": bool(relevant), "count": len(relevant), "sources": [item["source"] for item in relevant]}
