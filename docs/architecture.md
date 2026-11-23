# RelayIt Desk architecture

RelayIt uses a Router-to-Specialists workflow. The classifier normalizes and
classifies a ticket, the router selects exactly one specialist, and the
specialist invokes deterministic Python tools. Technical requests use local
document chunking and lexical retrieval, which is an honest credential-free
fallback for RAG. The escalation router preserves context in SQLite, and the
reviewer checks quality and evidence before release.

```mermaid
flowchart LR
  UI[Streamlit UI] --> WF[Support Workflow]
  WF --> C[Classifier Agent]
  C --> R[Router]
  R --> B[Billing Specialist]
  R --> T[Technical Specialist]
  R --> A[Account Specialist]
  B --> BT[Billing tools]
  T --> KB[Local technical KB]
  A --> AT[Account tools]
  B --> E[Escalation Router]
  T --> E
  A --> E
  WF --> V[Reviewer Agent]
  WF --> DB[(SQLite)]
```

Semantic Kernel is listed as the optional framework integration dependency and
is reported in the UI. Deterministic mode is the default and is labelled
clearly; no response is presented as an LLM response when credentials are not
configured.
