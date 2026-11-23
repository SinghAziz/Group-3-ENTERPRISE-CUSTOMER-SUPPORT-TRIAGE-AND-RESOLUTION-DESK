from __future__ import annotations

from relayit.tools.account_tools import check_account_access_policy, lookup_account


class AccountSpecialist:
    name = "Account Specialist"

    def run(self, ticket: dict, repository) -> dict:
        account = lookup_account(ticket["customer_email"])
        policy = check_account_access_policy(account)
        repository.add_tool(ticket["id"], self.name, "lookup_account", {"email": ticket["customer_email"]}, account)
        repository.add_tool(ticket["id"], self.name, "check_account_access_policy", account, policy)
        response = f"Thanks for contacting RelayIt Desk. {policy['guidance']}"
        return {"resolved": bool(account.get("found")), "resolution": str(policy["guidance"]),
                "response": response, "evidence": [account, policy]}
