from __future__ import annotations

from datetime import date

INVOICES = {
    "INV-1001": {"customer_email": "demo.billing@example.com", "amount": 199.0, "status": "paid", "date": "2026-01-15"},
    "INV-1002": {"customer_email": "demo.billing@example.com", "amount": 49.0, "status": "open", "date": "2026-02-01"},
}


def lookup_invoice(invoice_id: str | None, customer_email: str) -> dict[str, object]:
    if not invoice_id:
        return {"found": False, "reason": "No invoice identifier was supplied."}
    invoice = INVOICES.get(invoice_id.upper())
    if not invoice or invoice["customer_email"] != customer_email:
        return {"found": False, "reason": "Invoice was not found for this customer."}
    return {"found": True, "invoice_id": invoice_id.upper(), **invoice}


def evaluate_refund_eligibility(invoice: dict[str, object]) -> dict[str, object]:
    if not invoice.get("found"):
        return {"eligible": False, "decision": "escalate", "reason": str(invoice.get("reason"))}
    invoice_date = date.fromisoformat(str(invoice["date"]))
    age_days = (date.today() - invoice_date).days
    eligible = invoice["status"] == "paid" and age_days <= 30
    return {
        "eligible": eligible,
        "decision": "eligible" if eligible else "escalate",
        "reason": "Paid invoices within 30 days are eligible." if eligible else "The available refund rule does not allow an automatic refund.",
        "invoice_age_days": age_days,
    }
