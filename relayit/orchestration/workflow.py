from __future__ import annotations

from relayit.agents.account_specialist import AccountSpecialist
from relayit.agents.billing_specialist import BillingSpecialist
from relayit.agents.classifier import ClassifierAgent
from relayit.agents.escalation_router import EscalationRouter
from relayit.agents.reviewer import ReviewerAgent
from relayit.agents.technical_specialist import TechnicalSpecialist
from relayit.config import CONFIDENCE_THRESHOLD, MODEL_PROVIDER
from relayit.database.repository import Repository
from relayit.models.schemas import TicketInput, WorkflowResult


class SupportWorkflow:
    """Router-to-specialists workflow; deterministic mode is explicit and credential-free."""

    def __init__(self, repository: Repository | None = None):
        self.repository = repository or Repository()
        self.classifier = ClassifierAgent()
        self.specialists = {
            "billing": BillingSpecialist(),
            "technical": TechnicalSpecialist(),
            "account": AccountSpecialist(),
        }
        self.escalation = EscalationRouter()
        self.reviewer = ReviewerAgent()

    def run(self, ticket_input: TicketInput) -> WorkflowResult:
        customer_id = self.repository.customer(ticket_input.customer_name, ticket_input.customer_email)
        history = self.repository.history(customer_id)
        ticket_id = self.repository.create_ticket(customer_id, ticket_input.subject, ticket_input.description, ticket_input.priority)
        ticket = self.repository.ticket(ticket_id)
        assert ticket is not None
        trace: list[dict] = []

        def record(agent: str, action: str, result) -> None:
            self.repository.add_execution(ticket_id, agent, action, result)
            trace.append({"agent": agent, "action": action, "result": result})

        record("Workflow", "Received customer ticket", {"model_provider": MODEL_PROVIDER, "history_messages": len(history)})
        classification = self.classifier.run(ticket_input.subject, ticket_input.description)
        self.repository.update_ticket(ticket_id, category=classification["category"], confidence=classification["confidence"],
                                      rationale=classification["rationale"])
        record(self.classifier.name, "Classified ticket", classification)

        category = str(classification["category"])
        confidence = float(classification["confidence"])
        specialist = self.specialists.get(category)
        if confidence < CONFIDENCE_THRESHOLD or specialist is None:
            reason = "Classification confidence is below the configured threshold." if confidence < CONFIDENCE_THRESHOLD else "No specialist is configured for this category."
            escalation = self.escalation.run(ticket, reason, [], self.repository)
            record(self.escalation.name, "Escalated ticket", escalation)
            response = "A human support representative needs to review this request because we need more information before routing it safely."
            self.repository.update_ticket(ticket_id, specialist="Human Support", status="Escalated", resolution=reason, customer_response=response)
            review = self.reviewer.run(response, reason, [], self.repository, ticket_id)
            record(self.reviewer.name, "Reviewed escalation response", review)
            self.repository.add_conversation(customer_id, ticket_id, ticket_input.subject, ticket_input.description, response)
            return WorkflowResult(ticket_id, "Escalated", category, confidence, str(classification["rationale"]),
                                  "Human Support", reason, response, str(review["verdict"]), reason, [], trace, [])

        self.repository.update_ticket(ticket_id, specialist=specialist.name)
        record("Router", "Selected specialist", {"category": category, "specialist": specialist.name})
        specialist_result = specialist.run(ticket, self.repository)
        record(specialist.name, "Executed specialist tools and drafted response", specialist_result)
        response = str(specialist_result["response"])
        resolution = str(specialist_result["resolution"])
        evidence = list(specialist_result.get("evidence", []))
        if not specialist_result["resolved"]:
            reason = resolution
            escalation = self.escalation.run(ticket, reason, evidence, self.repository)
            record(self.escalation.name, "Escalated unresolved specialist result", escalation)
            status = "Awaiting Customer Information" if "provide" in response.lower() else "Escalated"
        else:
            reason = None
            status = "Resolved"
            record("Escalation Check", "No escalation required", {"status": status})
        review = self.reviewer.run(response, resolution, evidence, self.repository, ticket_id)
        record(self.reviewer.name, "Reviewed drafted response", review)
        if review["verdict"] != "Approved":
            status = "Escalated"
            reason = reason or "Reviewer requested revision because the response did not pass quality checks."
            escalation = self.escalation.run(ticket, reason, evidence, self.repository)
            record(self.escalation.name, "Escalated reviewer rejection", escalation)
        self.repository.update_ticket(ticket_id, status=status, resolution=resolution, customer_response=response)
        self.repository.add_conversation(customer_id, ticket_id, ticket_input.subject, ticket_input.description, response)
        return WorkflowResult(ticket_id, status, category, confidence, str(classification["rationale"]), specialist.name,
                              resolution, response, str(review["verdict"]), reason, evidence, trace, self.repository.tools(ticket_id))
