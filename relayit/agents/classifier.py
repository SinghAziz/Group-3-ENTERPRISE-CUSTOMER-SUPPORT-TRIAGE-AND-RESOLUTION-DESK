from __future__ import annotations

from relayit.tools.ticket_tools import normalize_ticket_text, validate_category


class ClassifierAgent:
    name = "Classifier Agent"

    def run(self, subject: str, description: str) -> dict:
        text = normalize_ticket_text(subject, description)
        keywords = {
            "billing": {"refund", "invoice", "payment", "charge", "billing", "paid"},
            "technical": {"error", "bug", "crash", "login", "api", "timeout", "install", "technical"},
            "account": {"account", "password", "access", "locked", "sign in", "mfa"},
        }
        scores = {category: sum(term in text for term in terms) for category, terms in keywords.items()}
        category = max(scores, key=scores.get)
        hits = scores[category]
        if hits == 0:
            category, confidence = "other", 0.35
            rationale = "No category-specific terms were found, so human clarification may be needed."
        else:
            confidence = min(0.96, 0.55 + hits * 0.12)
            rationale = f"Matched {hits} {category} signal(s) in normalized ticket text."
        validation = validate_category(category)
        return {"category": category, "confidence": round(confidence, 2), "rationale": rationale,
                "normalized_text": text, "validation": validation}
