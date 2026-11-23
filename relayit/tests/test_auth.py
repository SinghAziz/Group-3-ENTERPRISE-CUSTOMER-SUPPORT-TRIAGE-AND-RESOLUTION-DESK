from __future__ import annotations

import os
import unittest

from relayit.auth import AuthorizationError, User, authenticate, hash_password, verify_password
from relayit.database.repository import Repository


class AuthTests(unittest.TestCase):
    def test_password_hash_is_not_reversible_and_verifies(self):
        encoded = hash_password("correct horse battery staple")
        self.assertNotEqual(encoded, "correct horse battery staple")
        self.assertTrue(verify_password("correct horse battery staple", encoded))
        self.assertFalse(verify_password("wrong", encoded))

    def test_configured_user_authenticates_with_role(self):
        previous = os.environ.get("RELAYIT_AUTH_USERS_JSON")
        try:
            encoded = hash_password("secret")
            os.environ["RELAYIT_AUTH_USERS_JSON"] = (
                '{"reviewer":{"password_hash":"' + encoded + '","role":"reviewer"}}'
            )
            user = authenticate("reviewer", "secret")
            self.assertEqual(user.role, "reviewer")
        finally:
            if previous is None:
                os.environ.pop("RELAYIT_AUTH_USERS_JSON", None)
            else:
                os.environ["RELAYIT_AUTH_USERS_JSON"] = previous

    def test_analyst_cannot_review_escalation(self):
        with self.assertRaises(AuthorizationError):
            from relayit.auth import require_role
            require_role(User("analyst", "analyst"), "admin", "reviewer")

    def test_repository_requires_reviewer_for_human_review(self):
        repository = Repository(":memory:")
        with self.assertRaises(AuthorizationError):
            repository.add_human_review(
                1, "", "", "Escalated", "No unauthorized reply",
                User("analyst", "analyst"),
            )

    def test_repository_rejects_unauthenticated_ticket_reads(self):
        repository = Repository(":memory:")
        with self.assertRaises(AuthorizationError):
            repository.tickets()


if __name__ == "__main__":
    unittest.main()
