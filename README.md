# RelayIt Desk

**The right agent. The right answer.**

RelayIt Desk is a functional academic MVP for multi-agent enterprise support triage.
It receives a ticket, retrieves customer history, classifies it, routes it to a
billing, technical, or account specialist, invokes real Python tools, reviews the
draft, and persists the complete trace in SQLite.

## Requirements

- Python 3.11 or 3.12
- `pip` and `venv`
- A terminal and an up-to-date web browser

Python 3.14 is not the supported baseline for this project. An API key is not
required for the default deterministic demo.

## Agent roster

* **Classifier Agent** validates category and confidence.
* **Billing Specialist** looks up demonstration invoices and evaluates refund rules.
* **Technical Specialist** retrieves grounded chunks from `relayit/knowledge_base/technical`.
* **Account Specialist** checks demonstration account status and safe recovery policy.
* **Escalation Router** stores unresolved/low-confidence context for human review.
* **Reviewer Agent** checks tone, completeness, credentials safety, and evidence consistency.

The Router-to-Specialists design keeps deterministic business tools separate from
agent decisions and makes each execution auditable. SQLite stores customers,
tickets, conversations, messages, agent executions, tool executions, escalations,
reviewer results, and append-only audit entries.

## macOS or Linux setup

```bash
git clone <repository-url>
cd Group-3-ENTERPRISE-CUSTOMER-SUPPORT-TRIAGE-AND-RESOLUTION-DESK
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python -m unittest discover -s relayit/tests -p "test_*.py" -v
python -m streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
```

Open <http://localhost:8501> after Streamlit reports that the server is ready.
Stop the server with `Ctrl+C`.

If `python3.12` is unavailable, replace it with `python3.11`:

```bash
python3.11 -m venv .venv
```

## Windows setup (PowerShell)

```powershell
git clone <repository-url>
cd Group-3-ENTERPRISE-CUSTOMER-SUPPORT-TRIAGE-AND-RESOLUTION-DESK
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m unittest discover -s relayit/tests -p "test_*.py" -v
python -m streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501
```

Open <http://localhost:8501>.

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

## Configuration

The default `.env` configuration requires no hosted model or API credential:

```dotenv
RELAYIT_DB_PATH=relayit.db
RELAYIT_CONFIDENCE_THRESHOLD=0.62
RELAYIT_MODEL_PROVIDER=deterministic
OPENAI_API_KEY=
OPENAI_CHAT_MODEL=gpt-4o-mini
```

| Variable | Purpose | Default |
| --- | --- | --- |
| `RELAYIT_DB_PATH` | SQLite database location | `relayit.db` |
| `RELAYIT_CONFIDENCE_THRESHOLD` | Minimum confidence before escalation | `0.62` |
| `RELAYIT_MODEL_PROVIDER` | Agent execution mode | `deterministic` |
| `OPENAI_API_KEY` | Optional hosted model credential | Empty |
| `OPENAI_CHAT_MODEL` | Optional hosted model name | `gpt-4o-mini` |

Do not commit `.env` or a populated API key. The repository's `.gitignore` excludes
runtime databases and secret environment files.

## Run and demo

Use a new port if `8501` is busy:

```bash
python -m streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8587
```

Then open <http://localhost:8587>.

The **Create Ticket** page includes billing, technical, account, and honest
unknown-ticket examples. The **Ticket Details** view exposes classification,
retrieval evidence, tool output, reviewer verdict, and chronological trace.

Recommended live-demo sequence:

1. Open the Dashboard and show the empty or existing state.
2. Create a **Billing refund** ticket.
3. Open Ticket Details and explain classification, tool calls, and reviewer output.
4. Create a **Technical timeout** ticket to show grounded RAG retrieval.
5. Open the Escalation Queue and demonstrate a human review decision.
6. Use Agent Monitor to show persisted execution counts.

For a notebook-friendly workflow:

```bash
python notebooks/relayit_demo.py
```

To reset the demo database on macOS/Linux:

```bash
rm -f relayit.db
python -m streamlit run app.py
```

On Windows PowerShell:

```powershell
Remove-Item relayit.db -ErrorAction SilentlyContinue
python -m streamlit run app.py
```

## Tests

Run the complete unit test suite:

```bash
python -m unittest discover -s relayit/tests -p "test_*.py" -v
```

Tests use temporary SQLite databases and do not modify `relayit.db`.

## Project structure

```text
app.py                  Streamlit frontend
relayit/
  core/                 framework integration and shared agent logic
  database/             SQLite schema and repository
  knowledge_base/       demonstration RAG documents
  orchestration/        support workflow
  tools/                billing, account, and retrieval tools
  tests/                workflow and tool unit tests
docs/                   architecture documentation
notebooks/              demo notebook and script
.env.example            safe environment template
AGENTS.md               instructions for coding agents
```

## Troubleshooting

- **Port already in use:** choose a different `--server.port`.
- **Missing module:** activate `.venv`, then run
  `python -m pip install -r requirements.txt`.
- **Wrong Python version:** recreate `.venv` with Python 3.11 or 3.12.
- **Database is stale or corrupted:** stop Streamlit, remove `relayit.db`, and
  start the app again. This is a demonstration database and can be recreated.
- **Browser shows an old build:** stop the server, refresh with a hard reload,
  or open a private browser window.

## AI-assisted development

Coding agents should read `AGENTS.md` before changing this repository. They must
preserve deterministic demo behavior, keep credentials out of source control,
use isolated test databases, run the unit suite, and verify the Streamlit app
before reporting completion.

## Known MVP boundaries

The invoice, account, and knowledge-base records are local demonstration data.
There is no authentication, payment integration, external CRM, or production
multi-tenancy. Hosted LLM execution is optional and intentionally not claimed
by deterministic runs.
