"""
Ayiti-AI — Plateforme d'IA Souveraine Haïtienne.

Package principal exposant la version et les sous-modules.
"""
from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Ayiti-AI Team"
__description__ = "Sovereign Haitian Multimodal AI Platform"

# Sous-modules listés sans import eager (torch/peft chargés à la demande)
__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "data",
    "models",
    "training",
    "evaluation",
    "inference",
    "guardrails",
    "rag",
    "utils",
]

# Import lazy des sous-modules pour accès via ayiti_ai.data, ayiti_ai.models, etc.
def __getattr__(name: str):
    if name in __all__ and name not in ("__version__", "__author__", "__description__"):
        import importlib
        module = importlib.import_module(f"ayiti_ai.{name}")
        globals()[name] = module          # cache pour les accès suivants
        return module
    raise AttributeError(f"module 'ayiti_ai' has no attribute {name!r}")
