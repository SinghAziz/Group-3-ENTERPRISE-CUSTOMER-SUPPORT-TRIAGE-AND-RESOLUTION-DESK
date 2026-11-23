from __future__ import annotations

from relayit.tools.review_tools import evidence_consistency_check, response_quality_check


class ReviewerAgent:
    name = "Reviewer Agent"

    def run(self, response: str, resolution: str, evidence: list, repository, ticket_id: int) -> dict:
        quality = response_quality_check(response)
        consistency = evidence_consistency_check(response, evidence, resolution)
        verdict = "Approved" if quality["passed"] and consistency["supported"] else "Revision requested"
        result = {"verdict": verdict, "quality": quality, "consistency": consistency}
        repository.add_tool(ticket_id, self.name, "response_quality_check", response, quality)
        repository.add_tool(ticket_id, self.name, "evidence_consistency_check", {"response": response, "evidence": evidence}, consistency)
        repository.save_reviewer(ticket_id, verdict, result, consistency.get("unsupported_claims", []))
        return result
