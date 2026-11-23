from __future__ import annotations

"""Optional Semantic Kernel bridge.

The deterministic workflow remains the default so demos and tests never imply
an LLM was used. When credentials and a provider are configured, this module
is the single integration point for adding a Semantic Kernel service.
"""

from relayit.config import MODEL_PROVIDER


def framework_status() -> dict[str, str]:
    try:
        import semantic_kernel  # noqa: F401
    except ImportError:
        return {"framework": "Semantic Kernel", "status": "not installed", "mode": "deterministic"}
    return {"framework": "Semantic Kernel", "status": "available", "mode": MODEL_PROVIDER}
