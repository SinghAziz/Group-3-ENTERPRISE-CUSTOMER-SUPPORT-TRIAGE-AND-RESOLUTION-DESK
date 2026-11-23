from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from relayit.database.repository import Repository
from relayit.models.schemas import TicketInput
from relayit.orchestration.workflow import SupportWorkflow


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.repository = Repository(str(Path(self.directory.name) / "test.db"))
        self.workflow = SupportWorkflow(self.repository)

    def tearDown(self):
        self.directory.cleanup()

    def run_ticket(self, subject: str, description: str, email: str):
        return self.workflow.run(TicketInput("Test Customer", email, subject, description))

    def test_billing_refund_uses_two_tools(self):
        result = self.run_ticket("Refund invoice INV-1001", "Please refund this payment.", "demo.billing@example.com")
        self.assertEqual(result.category, "billing")
        self.assertIn(result.status, {"Resolved", "Awaiting Customer Information", "Escalated"})
        self.assertTrue(result.escalation_reason or result.resolution)
        self.assertGreaterEqual(len(result.tool_results), 4)

    def test_technical_ticket_retrieves_grounded_document(self):
        result = self.run_ticket("API timeout error", "The API returns a timeout.", "demo.tech@example.com")
        self.assertEqual(result.category, "technical")
        self.assertTrue(result.evidence)
        self.assertIn("demonstration", result.resolution.lower())

    def test_unknown_ticket_escalates(self):
        result = self.run_ticket("Question", "I need help with something unusual.", "other@example.com")
        self.assertEqual(result.status, "Escalated")
        self.assertIsNotNone(result.escalation_reason)

    def test_follow_up_reuses_customer_history(self):
        first = self.run_ticket("Cannot log in", "I cannot sign in.", "demo.account@example.com")
        second = self.run_ticket("Still locked", "The account is still locked.", "demo.account@example.com")
        self.assertEqual(first.category, "account")
        self.assertGreaterEqual(len(self.repository.history(self.repository.customer("Test Customer", "demo.account@example.com"))), 4)
        self.assertEqual(second.category, "account")

    def test_human_review_saves_customer_reply(self):
        result = self.run_ticket("Question", "I need help with something unusual.", "other@example.com")
        reply = "A support representative reviewed this and needs more details."
        self.repository.add_human_review(
            result.ticket_id,
            "Requested account reference",
            "Awaiting customer details",
            "Awaiting Customer Information",
            reply,
        )
        ticket = self.repository.ticket(result.ticket_id)
        self.assertEqual(ticket["status"], "Awaiting Customer Information")
        self.assertEqual(ticket["customer_response"], reply)
        customer_id = self.repository.customer("Test Customer", "other@example.com")
        history = self.repository.history(customer_id)
        self.assertTrue(any(message["role"] == "assistant" and reply in message["content"] for message in history))


if __name__ == "__main__":
    unittest.main()
