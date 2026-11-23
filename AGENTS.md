# RelayIt Desk - Agent Instructions

## Mission

Build and maintain a reliable, locally runnable academic MVP. Preserve the
multi-agent support workflow, the deterministic demonstration mode, and the
SQLite-backed audit trail.

## Before changing code

1. Inspect the relevant workflow, repository, tool, test, and frontend files.
2. Follow existing project patterns and keep changes focused.
3. Do not replace demonstration behavior with a hosted API unless the user
   explicitly requests that change.
4. Never commit `.env`, API keys, credentials, runtime databases, caches, or
   machine-specific paths.

## Implementation rules

- Keep the four core specialists and the reviewer traceable:
  classifier, billing/technical/account specialist, escalation router, reviewer.
- Keep deterministic tools separate from LLM or framework orchestration.
- Use `relayit/database/repository.py` for persistence; do not execute ad-hoc
  database writes from UI code.
- Update `app.py` only through focused Streamlit changes.
- Use Python 3.11 or 3.12-compatible syntax and dependencies.
- Do not claim that Semantic Kernel is active unless the provider and framework
  status confirm it.

## Required verification

Run the smallest relevant tests, then the complete unit suite:

```bash
python -m unittest discover -s relayit/tests -p "test_*.py" -v
```

For frontend or workflow changes, also start the app and verify it responds:

```bash
python -m streamlit run app.py --server.headless true --server.address 127.0.0.1 --server.port 8587
curl -I http://127.0.0.1:8587/_stcore/health
```

Stop or replace any temporary server before finishing. Do not leave a server
bound to an old project process or an unrelated port.

Authentication is mandatory. Never add default credentials. Generate hashes
with `python -m relayit.auth` and configure `RELAYIT_AUTH_USERS_JSON` locally.

## Demo database

Tests must use temporary SQLite databases. The application database is
`relayit.db` by default and is ignored by Git. To reset it for a live demo,
stop Streamlit and remove `relayit.db` before restarting.

## Documentation

Update `README.md` when setup, environment variables, commands, demo steps,
ports, or runtime behavior changes. Keep macOS/Linux and Windows instructions
accurate.

## Final response

Report:

1. What changed.
2. How to run or demo it.
3. Which tests passed.
4. The commit or diff status, if a commit was requested.