from __future__ import annotations


def package_escalation_context(ticket: dict, reason: str, evidence: list[dict]) -> dict[str, object]:
    return {"ticket_id": ticket["id"], "customer": ticket["customer_email"], "subject": ticket["subject"],
            "reason": reason, "evidence": evidence, "specialist": ticket.get("specialist")}


def create_escalation_record(repository, ticket_id: int, reason: str, context: dict) -> dict[str, object]:
    repository.escalate(ticket_id, reason, context)
    return {"created": True, "ticket_id": ticket_id, "reason": reason}
