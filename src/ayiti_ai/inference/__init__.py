"""Sous-module d'inférence Ayiti-AI : moteur de génération, chat CLI, streaming."""

__all__ = ["AyitiChat"]


def __getattr__(name: str):
    if name == "AyitiChat":
        from ayiti_ai.inference.chat import AyitiChat

        return AyitiChat
    raise AttributeError(f"module 'ayiti_ai.inference' has no attribute {name!r}")
