"""Sous-module d'évaluation Ayiti-AI : BLEU, ROUGE, BERTScore, perplexité, LLM judge."""

__all__ = [
    "compute_bleu",
    "compute_rouge",
    "compute_perplexity",
    "evaluate_model",
]


def __getattr__(name: str):
    if name in __all__:
        from ayiti_ai.evaluation import metrics as _m
        return getattr(_m, name)
    raise AttributeError(f"module 'ayiti_ai.evaluation' has no attribute {name!r}")
