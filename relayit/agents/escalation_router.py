from __future__ import annotations

from relayit.tools.escalation_tools import create_escalation_record, package_escalation_context


class EscalationRouter:
    name = "Escalation Router"

    def run(self, ticket: dict, reason: str, evidence: list, repository) -> dict:
        context = package_escalation_context(ticket, reason, evidence)
        result = create_escalation_record(repository, ticket["id"], reason, context)
        repository.add_tool(ticket["id"], self.name, "create_escalation_record", context, result)
        return {"escalated": True, "reason": reason, "context": context}
