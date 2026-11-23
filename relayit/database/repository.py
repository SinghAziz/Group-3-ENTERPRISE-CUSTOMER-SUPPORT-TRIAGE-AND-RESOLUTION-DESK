from __future__ import annotations

import json
import secrets
from typing import Any

from .db import connect, init_db, json_value


class Repository:
    def __init__(self, path: str | None = None):
        self.path = path
        init_db(path) if path else init_db()

    def customer(self, name: str, email: str) -> int:
        with connect(self.path) as db:
            row = db.execute("SELECT id FROM customers WHERE email = ?", (email,)).fetchone()
            if row:
                return row["id"]
            reference = f"RLY-{secrets.token_hex(4).upper()}"
            return db.execute(
                "INSERT INTO customers(name,email,reference) VALUES (?,?,?)",
                (name, email, reference),
            ).lastrowid

    def create_ticket(self, customer_id: int, subject: str, description: str, priority: str) -> int:
        with connect(self.path) as db:
            return db.execute(
                "INSERT INTO tickets(customer_id,subject,description,priority,status) VALUES (?,?,?,?,?)",
                (customer_id, subject, description, priority, "Processing"),
            ).lastrowid

    def update_ticket(self, ticket_id: int, **fields: Any) -> None:
        allowed = {"category", "confidence", "rationale", "specialist", "status", "resolution", "customer_response"}
        fields = {key: value for key, value in fields.items() if key in allowed}
        if not fields:
            return
        fields["updated_at"] = "CURRENT_TIMESTAMP"
        assignments = ", ".join(f"{key} = ?" if key != "updated_at" else f"{key} = CURRENT_TIMESTAMP" for key in fields)
        values = [value for key, value in fields.items() if key != "updated_at"]
        with connect(self.path) as db:
            db.execute(f"UPDATE tickets SET {assignments} WHERE id = ?", (*values, ticket_id))

    def add_execution(self, ticket_id: int, agent: str, action: str, result: Any = None, error: str | None = None) -> None:
        with connect(self.path) as db:
            db.execute(
                "INSERT INTO agent_executions(ticket_id,agent_name,action,result,error,completed_at) VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)",
                (ticket_id, agent, action, json_value(result) if result is not None else None, error),
            )
            db.execute(
                "INSERT INTO audit_logs(ticket_id,agent_name,action,result,error) VALUES (?,?,?,?,?)",
                (ticket_id, agent, action, json_value(result) if result is not None else None, error),
            )

    def add_tool(self, ticket_id: int, agent: str, tool: str, input_data: Any, output: Any, success: bool = True) -> None:
        with connect(self.path) as db:
            db.execute(
                "INSERT INTO tool_executions(ticket_id,agent_name,tool_name,input,output,success) VALUES (?,?,?,?,?,?)",
                (ticket_id, agent, tool, json_value(input_data), json_value(output), int(success)),
            )
            db.execute(
                "INSERT INTO audit_logs(ticket_id,agent_name,action,tool_called,tool_output,result) VALUES (?,?,?,?,?,?)",
                (ticket_id, agent, "Tool execution", tool, json_value(output), "success" if success else "failed"),
            )

    def add_conversation(self, customer_id: int, ticket_id: int, subject: str, description: str, response: str) -> None:
        with connect(self.path) as db:
            conversation_id = db.execute(
                "INSERT INTO conversations(customer_id,ticket_id) VALUES (?,?)", (customer_id, ticket_id)
            ).lastrowid
            db.executemany(
                "INSERT INTO messages(conversation_id,role,content) VALUES (?,?,?)",
                [(conversation_id, "customer", f"{subject}\n{description}"), (conversation_id, "assistant", response)],
            )

    def history(self, customer_id: int) -> list[dict[str, Any]]:
        with connect(self.path) as db:
            rows = db.execute(
                "SELECT m.role,m.content,m.created_at FROM messages m JOIN conversations c ON c.id=m.conversation_id WHERE c.customer_id=? ORDER BY m.created_at",
                (customer_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    def ticket(self, ticket_id: int) -> dict[str, Any] | None:
        with connect(self.path) as db:
            row = db.execute(
                "SELECT t.*,c.name customer_name,c.email customer_email,c.reference customer_reference FROM tickets t JOIN customers c ON c.id=t.customer_id WHERE t.id=?",
                (ticket_id,),
            ).fetchone()
            return dict(row) if row else None

    def tickets(self) -> list[dict[str, Any]]:
        with connect(self.path) as db:
            return [dict(row) for row in db.execute(
                "SELECT t.*,c.name customer_name,c.email customer_email FROM tickets t JOIN customers c ON c.id=t.customer_id ORDER BY t.created_at DESC"
            ).fetchall()]

    def executions(self, ticket_id: int) -> list[dict[str, Any]]:
        with connect(self.path) as db:
            return [dict(row) for row in db.execute("SELECT * FROM agent_executions WHERE ticket_id=? ORDER BY id", (ticket_id,)).fetchall()]

    def tools(self, ticket_id: int) -> list[dict[str, Any]]:
        with connect(self.path) as db:
            return [dict(row) for row in db.execute("SELECT * FROM tool_executions WHERE ticket_id=? ORDER BY id", (ticket_id,)).fetchall()]

    def reviewer(self, ticket_id: int) -> dict[str, Any] | None:
        with connect(self.path) as db:
            row = db.execute("SELECT * FROM reviewer_results WHERE ticket_id=? ORDER BY id DESC LIMIT 1", (ticket_id,)).fetchone()
            return dict(row) if row else None

    def save_reviewer(self, ticket_id: int, verdict: str, checklist: Any, unsupported: Any) -> None:
        with connect(self.path) as db:
            db.execute("INSERT INTO reviewer_results(ticket_id,verdict,checklist,unsupported_claims) VALUES (?,?,?,?)",
                       (ticket_id, verdict, json_value(checklist), json_value(unsupported)))

    def escalate(self, ticket_id: int, reason: str, evidence: Any) -> None:
        with connect(self.path) as db:
            db.execute("INSERT OR REPLACE INTO escalations(ticket_id,reason,evidence) VALUES (?,?,?)",
                       (ticket_id, reason, json_value(evidence)))

    def escalations(self) -> list[dict[str, Any]]:
        with connect(self.path) as db:
            return [dict(row) for row in db.execute(
                "SELECT e.*,t.subject,t.description,t.priority,t.specialist,c.name customer_name FROM escalations e JOIN tickets t ON t.id=e.ticket_id JOIN customers c ON c.id=t.customer_id ORDER BY e.created_at DESC"
            ).fetchall()]

    def add_human_review(self, ticket_id: int, note: str, decision: str, status: str, customer_reply: str) -> None:
        customer_reply = customer_reply.strip()
        if not customer_reply:
            raise ValueError("A customer-facing reply is required.")
        with connect(self.path) as db:
            db.execute("UPDATE escalations SET internal_note=?,human_decision=?,resolved_at=CURRENT_TIMESTAMP WHERE ticket_id=?",
                       (note, decision, ticket_id))
            db.execute(
                "UPDATE tickets SET status=?,resolution=?,customer_response=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (status, decision or "Reviewed by a human support representative", customer_reply, ticket_id),
            )
            conversation = db.execute(
                "SELECT id FROM conversations WHERE ticket_id=? ORDER BY id DESC LIMIT 1",
                (ticket_id,),
            ).fetchone()
            if conversation:
                db.execute(
                    "INSERT INTO messages(conversation_id,role,content) VALUES (?,?,?)",
                    (conversation["id"], "assistant", customer_reply),
                )
            db.execute(
                "INSERT INTO audit_logs(ticket_id,agent_name,action,result) VALUES (?,?,?,?)",
                (ticket_id, "Human Support", "Customer reply", customer_reply),
            )

    def stats(self) -> dict[str, Any]:
        tickets = self.tickets()
        counts = {}
        for ticket in tickets:
            counts[ticket["status"]] = counts.get(ticket["status"], 0) + 1
        return {"total": len(tickets), "counts": counts, "categories": self._category_counts(tickets)}

    @staticmethod
    def _category_counts(tickets: list[dict[str, Any]]) -> dict[str, int]:
        result: dict[str, int] = {}
        for ticket in tickets:
            category = ticket["category"] or "Unclassified"
            result[category] = result.get(category, 0) + 1
        return result
