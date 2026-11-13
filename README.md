# Group-3-ENTERPRISE-CUSTOMER-SUPPORT-TRIAGE-AND-RESOLUTION-DESK

#RelayIt
Objective
To design, build and demonstrate a multi-agent system that automates an enterprise workflow
by applying a defined coordination architecture, framework-based agent development
(Microsoft Agent Framework or Semantic Kernel), grounded retrieval or shared memory, and
collaborative task execution across specialised agents.

What to do
Build a multi-agent system to take an incoming support ticket, route it to the right specialist,
resolve it or escalate, and draft the customer reply. Create the following agents, each as a
separate module: Classifier Agent (reads the ticket and labels it (billing, technical, account, or
other) with confidence), Billing Specialist (handles refund and invoice questions using a billingrules tool), Technical Specialist (handles how-to and error tickets using a RAG knowledge
base), Account Specialist (handles login and access tickets), Escalation Router (if confidence is
low or the specialist cannot resolve, routes to a human queue and explains why). Coordinate
them using a router to specialists architecture. RAG over a support knowledge-base for the
Technical Specialist; conversation memory so a follow-up ticket from the same user has
context. The system must output the chosen category, the specialist's resolution, and a drafted
customer-facing reply, or a tagged escalation.
Group of three: Add a satisfaction-check loop: after drafting the reply, a Reviewer Agent
checks tone and completeness before the reply is released.
