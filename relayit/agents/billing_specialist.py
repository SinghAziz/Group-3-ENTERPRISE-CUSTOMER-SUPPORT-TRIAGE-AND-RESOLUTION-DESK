from __future__ import annotations

import re

from relayit.tools.billing_tools import evaluate_refund_eligibility, lookup_invoice


class BillingSpecialist:
    name = "Billing Specialist"

    def run(self, ticket: dict, repository) -> dict:
        match = re.search(r"\bINV-\d+\b", f"{ticket['subject']} {ticket['description']}", re.I)
        invoice = lookup_invoice(match.group(0) if match else None, ticket["customer_email"])
        decision = evaluate_refund_eligibility(invoice)
        repository.add_tool(ticket["id"], self.name, "lookup_invoice", {"invoice_id": match.group(0) if match else None}, invoice)
        repository.add_tool(ticket["id"], self.name, "evaluate_refund_eligibility", invoice, decision)
        if decision["decision"] == "eligible":
            resolution = f"Invoice {invoice['invoice_id']} is eligible for a refund under the available rule."
            response = f"Thanks for contacting RelayIt Desk. We verified {invoice['invoice_id']}. {decision['reason']} A support representative can now process the refund."
            return {"resolved": True, "resolution": resolution, "response": response, "evidence": [invoice, decision]}
        return {"resolved": False, "resolution": str(decision["reason"]),
                "response": "We could not verify automatic refund eligibility from the information available. Please provide the invoice ID so a support representative can review it.", "evidence": [invoice, decision]}
