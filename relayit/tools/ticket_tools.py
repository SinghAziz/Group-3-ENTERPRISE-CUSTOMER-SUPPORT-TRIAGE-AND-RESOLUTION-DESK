from __future__ import annotations

import re


def normalize_ticket_text(subject: str, description: str) -> str:
    return re.sub(r"\s+", " ", f"{subject}. {description}".strip()).lower()


def validate_category(category: str) -> dict[str, object]:
    valid = {"billing", "technical", "account", "other"}
    return {"category": category, "valid": category in valid, "allowed": sorted(valid)}
