"""Notebook-friendly demo script; run with `python notebooks/relayit_demo.py`."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from relayit.database.repository import Repository
from relayit.models.schemas import TicketInput
from relayit.orchestration.workflow import SupportWorkflow

workflow = SupportWorkflow(Repository())
tickets = [
    TicketInput("Demo Billing", "demo.billing@example.com", "Refund invoice INV-1001", "I need a refund."),
    TicketInput("Demo Technical", "demo.tech@example.com", "API timeout error", "Requests time out."),
    TicketInput("Demo Account", "demo.account@example.com", "Cannot log in", "I cannot sign in."),
    TicketInput("Demo Unknown", "unknown@example.com", "Something unusual", "Please help with an unlisted issue."),
]
for ticket in tickets:
    result = workflow.run(ticket)
    print(f"\nTicket #{result.ticket_id}: {result.status} ({result.category})")
    for event in result.trace:
        print(f"  {event['agent']}: {event['action']}")
    print("Response:", result.customer_response)
