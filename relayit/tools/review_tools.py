from __future__ import annotations


def response_quality_check(response: str) -> dict[str, object]:
    checks = {
        "has_response": bool(response.strip()),
        "has_next_step": any(word in response.lower() for word in ("next", "please", "contact", "use")),
        "safe_credentials": not any(word in response.lower() for word in ("password is", "mfa code is", "api key is")),
        "professional_tone": not response.strip().startswith(("!!!", "???")),
    }
    return {"checks": checks, "passed": all(checks.values())}


def evidence_consistency_check(response: str, evidence: list[dict], resolution: str) -> dict[str, object]:
    if not evidence:
        return {"supported": True, "unsupported_claims": []}
    claims = [sentence.strip() for sentence in response.split(".") if sentence.strip()]
    unsupported = [claim for claim in claims if "password is" in claim.lower() or "mfa code is" in claim.lower()]
    return {"supported": not unsupported, "unsupported_claims": unsupported, "resolution_present": bool(resolution.strip())}
