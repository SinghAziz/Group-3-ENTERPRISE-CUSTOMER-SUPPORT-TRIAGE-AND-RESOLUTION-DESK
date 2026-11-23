from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TicketInput:
    customer_name: str
    customer_email: str
    subject: str
    description: str
    priority: str = "Medium"


@dataclass
class WorkflowResult:
    ticket_id: int
    status: str
    category: str
    confidence: float
    rationale: str
    specialist: str
    resolution: str
    customer_response: str
    reviewer_verdict: str
    escalation_reason: str | None = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    tool_results: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
