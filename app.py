from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from relayit.core.framework import framework_status
from relayit.database.repository import Repository
from relayit.models.schemas import TicketInput
from relayit.orchestration.workflow import SupportWorkflow

st.set_page_config(page_title="RelayIt Desk", page_icon="✦", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700&display=swap');
:root { --ink:#17212b; --muted:#68727d; --line:#e6e9e6; --paper:#f7f8f5; --panel:#ffffff; --coral:#ef6a5b; --mint:#dceadf; --teal:#287b72; }
html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
.stApp { background:var(--paper); color:var(--ink); }
.block-container { max-width:1320px; padding-top:1.8rem; padding-bottom:3rem; }
[data-testid="stSidebar"] { background:#17212b; border-right:0; }
[data-testid="stSidebar"] * { color:#f7f8f5; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding:.72rem .8rem; border-radius:7px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) { background:#26343f; }
h1, h2, h3 { font-family:'Manrope', sans-serif; color:var(--ink); letter-spacing:0; }
h1 { font-size:2.1rem; margin-bottom:.25rem; }
[data-testid="stCaptionContainer"] { color:var(--muted); }
.metric-card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px 18px; min-height:108px; }
.metric-card small { color:var(--muted); font-size:.78rem; font-weight:600; text-transform:uppercase; letter-spacing:.08em; }
.metric-card h2 { margin:.35rem 0 0; font-size:1.8rem; }
.trace { border:1px solid var(--line); border-left:3px solid var(--teal); border-radius:6px; padding:12px 14px; margin:8px 0; background:#fff; }
.status-pill { display:inline-block; border-radius:999px; padding:.28rem .65rem; font-size:.76rem; font-weight:700; }
.status-resolved { background:#dceadf; color:#27705a; }
.status-escalated { background:#fee1dc; color:#a2463a; }
.status-processing { background:#edf0e8; color:#59636a; }
.status-info { background:#fff0c9; color:#84651e; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:8px; overflow:hidden; }
[data-testid="stForm"] { border:1px solid #dfe4df; border-radius:12px; background:#fff; padding:24px; box-shadow:0 6px 22px rgba(23,33,43,.04); }
[data-testid="stTextInput"] label, [data-testid="stTextArea"] label, [data-testid="stSelectbox"] label { color:#17212b !important; font-weight:700; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  background:#fff !important;
  color:#17212b !important;
  border-radius:7px !important;
  border:1px solid #cfd6cf !important;
  -webkit-text-fill-color:#17212b;
  caret-color:#17212b;
}
[data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {
  color:#7b858f !important;
  -webkit-text-fill-color:#7b858f;
  opacity:1;
}
[data-testid="stTextArea"] textarea { min-height:132px; line-height:1.55; font-size:.96rem; }
[data-testid="stTextInput"]:focus-within input, [data-testid="stTextArea"]:focus-within textarea,
[data-testid="stSelectbox"]:focus-within div[data-baseweb="select"] > div { border-color:#287b72 !important; box-shadow:0 0 0 3px rgba(40,123,114,.12) !important; }
.stButton button { border-radius:7px; border:1px solid #ccd2cd; color:var(--ink); min-height:42px; }
.stButton button[kind="primary"] { background:#e95f50; border-color:#e95f50; color:#fff; font-weight:700; padding:.55rem 1.15rem; }
.stButton button[kind="primary"]:hover { background:#d95346; border-color:#d95346; color:#fff; }
[data-testid="stSidebar"] .stButton button { border:1px solid #3b4a55; color:#fff; background:transparent; }
.page-intro { border:1px solid #e4e8e3; background:linear-gradient(135deg,#fff 0%,#f2f6f2 100%);
  border-radius:12px; padding:18px 22px; margin-bottom:18px; }
.page-intro h1 { margin:0 0 4px; }
.page-intro p { color:#68727d; margin:0; }
.form-section { color:#68727d; font-size:.78rem; font-weight:700; letter-spacing:.08em;
  text-transform:uppercase; padding-top:4px; margin-bottom:-2px; }
.helper-text { color:#68727d; font-size:.84rem; margin-top:-12px; margin-bottom:10px; }
</style>
""", unsafe_allow_html=True)

repo = Repository()


def metric(label: str, value: str) -> None:
    st.markdown(f'<div class="metric-card"><small>{label}</small><h2>{value}</h2></div>', unsafe_allow_html=True)


def status_html(status: str) -> str:
    key = {
        "Resolved": "resolved",
        "Escalated": "escalated",
        "Processing": "processing",
        "Awaiting Customer Information": "info",
    }.get(status, "processing")
    return f'<span class="status-pill status-{key}">{status}</span>'


def ticket_details(ticket_id: int) -> None:
    ticket = repo.ticket(ticket_id)
    if not ticket:
        st.error("Ticket not found.")
        return
    st.header(f"Ticket #{ticket_id} · {ticket['subject']}")
    columns = st.columns(4)
    for column, (label, value) in zip(columns, [("Status", ticket["status"]), ("Category", ticket["category"] or "—"),
                                                 ("Confidence", f"{ticket['confidence']:.0%}" if ticket["confidence"] else "—"),
                                                 ("Specialist", ticket["specialist"] or "—")]):
        with column:
            metric(label, str(value))
    st.write(f"**Customer:** {ticket['customer_name']} · {ticket['customer_email']}")
    st.write(f"**Classification rationale:** {ticket['rationale'] or '—'}")
    if ticket["resolution"]:
        st.subheader("Resolution")
        st.write(ticket["resolution"])
    if ticket["customer_response"]:
        st.subheader("Customer response")
        st.info(ticket["customer_response"])
    review = repo.reviewer(ticket_id)
    if review:
        st.subheader("Reviewer verdict")
        st.write(review["verdict"])
        st.json(json.loads(review["checklist"]))
    st.subheader("Execution trace")
    for execution in repo.executions(ticket_id):
        st.markdown(f'<div class="trace"><b>{execution["agent_name"]}</b> · {execution["action"]}<br><small>{execution["completed_at"]}</small></div>', unsafe_allow_html=True)
        if execution["result"]:
            with st.expander("Output"):
                st.json(json.loads(execution["result"]))
    st.subheader("Tool executions")
    for tool in repo.tools(ticket_id):
        with st.expander(f"{tool['agent_name']} · {tool['tool_name']}"):
            st.json(json.loads(tool["output"]))


def dashboard() -> None:
    st.title("RelayIt Desk")
    st.caption("Multi-agent customer-support triage")
    stats = repo.stats()
    tickets = repo.tickets()
    total = stats["total"]
    counts = stats["counts"]
    cols = st.columns(5)
    for col, label, value in zip(cols, ["Total tickets", "Resolved", "Escalated", "Awaiting info", "Resolution rate"],
                                  [total, counts.get("Resolved", 0), counts.get("Escalated", 0),
                                   counts.get("Awaiting Customer Information", 0),
                                   f"{counts.get('Resolved', 0) / total:.0%}" if total else "0%"]):
        with col:
            metric(label, str(value))

    left, right = st.columns([1, 1.7])
    with left:
        st.subheader("Category mix")
        if stats["categories"]:
            fig = px.bar(
                x=list(stats["categories"].values()),
                y=list(stats["categories"].keys()),
                orientation="h",
                color=list(stats["categories"].keys()),
                color_discrete_sequence=["#287b72", "#ef6a5b", "#e7b54a", "#7a8390"],
            )
            fig.update_layout(template="plotly_white", height=280, showlegend=False,
                              margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
            fig.update_xaxes(title=None, gridcolor="#edf0ec", tick0=0, dtick=1)
            fig.update_yaxes(title=None)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No classifications yet.")

    with right:
        st.subheader("Recent ticket activity")
        if tickets:
            frame = pd.DataFrame(tickets).head(8)
            st.dataframe(
                frame[["id", "subject", "customer_name", "category", "priority", "status", "created_at"]],
                hide_index=True,
                width="stretch",
                column_config={
                    "id": st.column_config.NumberColumn("Ticket", format="#%d"),
                    "subject": st.column_config.TextColumn("Subject", width="large"),
                    "customer_name": "Customer",
                    "category": "Category",
                    "priority": "Priority",
                    "status": "Status",
                    "created_at": st.column_config.DatetimeColumn("Created", format="MMM DD, HH:mm"),
                },
            )
        else:
            st.info("Create a ticket to begin the live workflow.")

    st.subheader("Agent activity")
    executions = [item for ticket in tickets for item in repo.executions(ticket["id"])]
    if executions:
        frame = pd.DataFrame(executions)
        counts_frame = frame.groupby("agent_name").size().reset_index(name="executions").sort_values("executions", ascending=False)
        st.dataframe(counts_frame, hide_index=True, width="stretch")
    st.caption(f"Execution mode: {framework_status()['mode']} · framework status: {framework_status()['status']}")


def inbox() -> None:
    st.title("Ticket Inbox")
    tickets = repo.tickets()
    query = st.text_input("Search tickets")
    status = st.selectbox("Filter status", ["All", "Resolved", "Escalated", "Awaiting Customer Information", "Processing"])
    filtered = [ticket for ticket in tickets if (status == "All" or ticket["status"] == status) and
                (not query or query.lower() in str(ticket).lower())]
    st.dataframe(pd.DataFrame(filtered)[["id", "customer_name", "subject", "category", "priority", "specialist", "status", "created_at"]]
                 if filtered else pd.DataFrame(), hide_index=True, width="stretch")
    for ticket in filtered:
        if st.button(f"Open #{ticket['id']} · {ticket['subject']}", key=f"open-{ticket['id']}"):
            st.session_state["selected_ticket"] = ticket["id"]
            st.rerun()


def create_ticket() -> None:
    st.markdown("""
    <div class="page-intro">
      <h1>Tell us what happened</h1>
      <p>Share the details below. RelayIt will classify the issue and route it to the right specialist.</p>
    </div>
    """, unsafe_allow_html=True)
    examples = {
        "Custom": ("", ""),
        "Billing refund": ("Refund for invoice INV-1001", "I was charged and would like a refund."),
        "Technical timeout": ("API timeout error", "Our API request returns a timeout."),
        "Account login": ("Cannot log in", "I cannot sign in to my account."),
    }
    example = st.selectbox("Start with an example", list(examples), help="Choosing an example pre-fills the form. You can edit every field.")
    default_subject, default_description = examples[example]
    with st.form("create-ticket"):
        st.markdown('<div class="form-section">Customer</div>', unsafe_allow_html=True)
        customer_col, email_col = st.columns(2)
        with customer_col:
            name = st.text_input("Name", "Demo Customer", placeholder="Your full name")
        with email_col:
            email = st.text_input("Email", "demo.billing@example.com", placeholder="you@company.com")

        st.markdown('<div class="form-section">Issue details</div>', unsafe_allow_html=True)
        subject = st.text_input("Subject", default_subject, max_chars=120, placeholder="Briefly summarize the issue")
        st.markdown('<div class="helper-text">Use a short, specific title so the support team can find this quickly.</div>', unsafe_allow_html=True)
        description = st.text_area(
            "What happened?",
            default_description,
            height=150,
            max_chars=3000,
            placeholder="Describe what you tried, what happened, and any error message or invoice number you saw.",
        )

        st.markdown('<div class="form-section">Priority</div>', unsafe_allow_html=True)
        priority = st.selectbox(
            "How urgent is this?",
            ["Low", "Medium", "High", "Urgent"],
            index=1,
            help="Use Urgent only when work is blocked or a service outage is affecting customers.",
        )
        submitted = st.form_submit_button("Submit ticket", type="primary", width="stretch")
    if submitted:
        if not name.strip() or not email.strip() or not subject.strip() or not description.strip():
            st.error("Complete all fields.")
            return
        result = SupportWorkflow(repo).run(TicketInput(name, email, subject, description, priority))
        st.success(f"Ticket #{result.ticket_id} completed: {result.status}")
        st.session_state["selected_ticket"] = result.ticket_id
        st.session_state["page"] = "Ticket Details"
        st.rerun()


def escalations() -> None:
    st.title("Escalation Queue")
    items = repo.escalations()
    if not items:
        st.success("No escalated tickets.")
    for item in items:
        with st.expander(f"#{item['ticket_id']} · {item['subject']} · {item['reason']}"):
            st.write(f"**Customer:** {item['customer_name']} · **Specialist:** {item['specialist']}")
            st.write(f"**Evidence:** {item['evidence']}")
            with st.form(f"review-{item['ticket_id']}"):
                note = st.text_area("Internal note")
                decision = st.text_input("Human decision")
                new_status = st.selectbox("Update status", ["Resolved", "Awaiting Customer Information", "Escalated"])
                if st.form_submit_button("Save human review"):
                    repo.add_human_review(item["ticket_id"], note, decision, new_status)
                    st.rerun()


def monitor() -> None:
    st.title("Agent Monitor")
    tickets = repo.tickets()
    rows = []
    for ticket in tickets:
        for execution in repo.executions(ticket["id"]):
            rows.append(execution)
    frame = pd.DataFrame(rows)
    if frame.empty:
        st.info("Run a ticket workflow to populate the monitor.")
    else:
        st.dataframe(frame.groupby("agent_name").agg(executions=("id", "count"), recent_activity=("completed_at", "max")).reset_index(),
                     hide_index=True, width="stretch")


with st.sidebar:
    st.markdown("## ✦ RelayIt Desk")
    pages = ["Dashboard", "Ticket Inbox", "Create Ticket", "Escalation Queue", "Agent Monitor"]
    if st.session_state.get("selected_ticket"):
        pages.append("Ticket Details")
    default_page = st.session_state.get("page", "Dashboard")
    page_index = pages.index(default_page) if default_page in pages else 0
    page = st.radio("Navigate", pages, index=page_index)
    st.session_state["page"] = page
    st.caption("Deterministic demonstration mode is clearly labelled and uses real SQLite-backed tools.")

if page == "Dashboard":
    dashboard()
elif page == "Ticket Inbox":
    inbox()
elif page == "Create Ticket":
    create_ticket()
elif page == "Escalation Queue":
    escalations()
elif page == "Agent Monitor":
    monitor()
else:
    ticket_details(st.session_state["selected_ticket"])
