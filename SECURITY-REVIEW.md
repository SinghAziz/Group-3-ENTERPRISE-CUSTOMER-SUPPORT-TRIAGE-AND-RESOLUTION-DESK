# Security Review Summary

Review date: 2026-11-23

## Executive summary

The repository was reviewed for authentication, authorization, database access,
unsafe HTML, secrets, AI/LLM integration, dependency risk, and deployment
configuration. One confirmed high-severity issue was found: the application
exposes customer and administrative workflows without authentication or
role-based authorization.

The review did not confirm SQL injection, active prompt-injection/LLM tool
execution, or populated credential exposure. These areas remain potential
production risks and require continued security controls.

## Findings

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 1 | 🟠 HIGH | app.py | 142-146, 269-301, 319-345 | Missing authentication and authorization; all dashboard, ticket, trace, escalation, and human-review workflows are accessible to any reachable user | 10/10 |

## Confirmed finding

### 1. Missing authentication and role-based authorization

- **Severity:** High
- **CWE:** CWE-862, Missing Authorization
- **Affected files:**
  - [app.py](app.py) (ticket and escalation UI)
  - [README.md](README.md:44)
  - [README.md](README.md:67)
  - [AGENTS.md](AGENTS.md)

**Evidence**

The Streamlit application directly renders dashboard, ticket inbox, ticket
details, escalation queue, agent monitor, and human-review controls without an
authentication check or role gate. The escalation workflow can update ticket
status, internal notes, decisions, and customer-facing replies. There is no
user identity or role lookup in the UI or repository layer.

Setup documentation uses `--server.address 0.0.0.0`, making loopback-only
binding insufficient by default if the documented command is used. The README
also identifies the MVP as lacking authentication.

**Attack scenario**

An unauthenticated person who can reach the host opens the Streamlit UI and
reads customer names, email addresses, ticket descriptions, execution traces,
tool outputs, and escalation evidence. The same person can submit a human
decision or customer reply.

**Impact**

- Unauthorized disclosure of customer and support data.
- Unauthorized ticket and escalation modifications.
- Incorrect or fraudulent customer communications.
- Loss of accountability and integrity of the audit trail.

**Recommended remediation**

1. Require authentication at the reverse proxy or application boundary.
2. Centralize identity and role checks in server-side code.
3. Define at least customer, analyst, human-reviewer, and administrator roles.
4. Restrict ticket reads and mutations to authorized assignments or tenants.
5. Require human-reviewer role for escalation decisions and customer replies.
6. Keep binding on loopback for local development and require explicit,
   authenticated production deployment configuration.
7. Add server-side session isolation and security tests for every protected route.

**Status**

Unresolved. No remediation was implemented in this summary-only follow-up.

## Other review results

### SQL injection

Not confirmed as a current exploitable finding. SQL queries in
`relayit/database/repository.py` use parameter placeholders, and dynamic
`UPDATE` fields are filtered by an allowlist. SQL-layer authorization remains
absent because the application has no user identity model.

### Unsafe HTML and XSS

The application uses `unsafe_allow_html=True` in [app.py](app.py:83),
[app.py](app.py:132), and [app.py](app.py:227). Several database-backed values
are rendered or interpolated. The reviewed current HTML paths did not establish
a confirmed executable XSS primitive, but untrusted ticket descriptions and
email/customer values should not be considered safely encoded merely because
current output was internally formatted.

Recommended controls:

- Replace `unsafe_allow_html` for ordinary text and metrics with native
  Streamlit components.
- HTML-escape any unavoidable database-derived value.
- Apply a restrictive Content Security Policy where the deployment supports it.

### Secrets

No populated hardcoded API key or credential was found in the inspected source
and environment template. `.env` is ignored, but production secret handling,
Git history, CI variables, and runtime logs were not established as secure.

### AI/LLM security

No active hosted-LLM prompt/tool path was confirmed. The default
`RELAYIT_MODEL_PROVIDER=deterministic` path uses local tools. Semantic Kernel
is present as an optional integration, so prompt-injection, sensitive-data
disclosure, tool abuse, and output-validation controls should still be
implemented before activating hosted models.

### Dependencies

Dependencies use version ranges and the repository did not contain a lockfile.
This creates reproducibility and unpinned dependency risk. A package vulnerability
scan should be run with `pip-audit` before production deployment.

### Privacy and audit logging

Customer names, email addresses, ticket descriptions, internal traces, tool
results, and escalation evidence are stored in SQLite. The database is
demonstration data by default, but the model requires access controls and
retention/deletion controls before real PII is processed.

## Verification performed

- Repository structure and Python entry points reviewed.
- Streamlit UI and escalation workflow reviewed.
- Database schema and repository queries reviewed.
- Environment template and configuration reviewed.
- Existing security review: 8/8 unit tests passed.
- No external penetration testing or credential-harvesting activity performed.

## Remaining risks

- Production authentication and RBAC are not implemented.
- Streamlit UI access controls are not a substitute for reverse-proxy or app
  identity controls.
- Public binding must not be used before authentication.
- Existing user-controlled HTML and database values need a focused XSS review.
- AI provider safeguards are absent until a hosted model is enabled.
- Dependency lock and vulnerability automation are not established.

## Final readiness

**Not ready for production use with real customer data.** The confirmed
missing authorization issue is sufficient to prevent production readiness.
