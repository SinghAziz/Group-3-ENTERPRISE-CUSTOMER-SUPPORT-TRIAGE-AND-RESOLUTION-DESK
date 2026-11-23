from __future__ import annotations

from relayit.tools.retrieval_tools import evaluate_relevance, search_knowledge_base


class TechnicalSpecialist:
    name = "Technical Specialist"

    def run(self, ticket: dict, repository) -> dict:
        query = f"{ticket['subject']} {ticket['description']}"
        results = search_knowledge_base(query)
        relevance = evaluate_relevance(results)
        repository.add_tool(ticket["id"], self.name, "search_knowledge_base", {"query": query}, results)
        repository.add_tool(ticket["id"], self.name, "evaluate_relevance", {"results": len(results)}, relevance)
        if not relevance["relevant"]:
            return {"resolved": False, "resolution": "The demonstration knowledge base does not contain a relevant answer.",
                    "response": "We could not find grounded troubleshooting guidance for this issue. A technical support representative should review it.",
                    "evidence": results}
        guidance = results[0]["content"]
        response = f"Thanks for contacting RelayIt Desk. Based on our demonstration support documentation:\n\n{guidance}\n\nPlease try these steps and reply with the result."
        return {"resolved": True, "resolution": guidance, "response": response, "evidence": results}
