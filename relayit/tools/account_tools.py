from __future__ import annotations

ACCOUNTS = {
    "demo.account@example.com": {"status": "active", "mfa_enabled": True, "plan": "Enterprise"},
    "locked.account@example.com": {"status": "locked", "mfa_enabled": True, "plan": "Standard"},
}


def lookup_account(email: str) -> dict[str, object]:
    account = ACCOUNTS.get(email.lower())
    return {"found": bool(account), **(account or {"reason": "No demonstration account matches this email."})}


def check_account_access_policy(account: dict[str, object]) -> dict[str, object]:
    if not account.get("found"):
        return {"allowed": False, "guidance": "Verify the customer reference through a human support representative."}
    if account["status"] == "locked":
        return {"allowed": True, "guidance": "Use the password-reset flow, then contact support if the account remains locked."}
    return {"allowed": True, "guidance": "Use the password-reset flow and complete MFA. Never share a password or MFA code."}
