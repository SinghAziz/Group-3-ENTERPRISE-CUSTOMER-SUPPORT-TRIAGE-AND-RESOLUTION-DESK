from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from relayit.database.db import connect, init_db

from relayit.tools.billing_tools import evaluate_refund_eligibility, lookup_invoice
from relayit.tools.review_tools import response_quality_check


class ToolTests(unittest.TestCase):
    def test_unknown_invoice_never_claims_eligibility(self):
        invoice = lookup_invoice("INV-9999", "nobody@example.com")
        self.assertFalse(evaluate_refund_eligibility(invoice)["eligible"])

    def test_reviewer_rejects_empty_response(self):
        self.assertFalse(response_quality_check("").get("passed"))


class DatabaseTests(unittest.TestCase):
    def test_connection_is_closed_after_context_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "test.db")
            init_db(path)

            with connect(path) as connection:
                connection.execute(
                    "INSERT INTO customers(name,email,reference) VALUES (?,?,?)",
                    ("Test Customer", "test@example.com", "RLY-TEST"),
                )

            with self.assertRaises(sqlite3.ProgrammingError):
                connection.execute("SELECT 1")


if __name__ == "__main__":
    unittest.main()
