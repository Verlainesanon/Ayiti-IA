from typing import Optional, Protocol
from pydantic import BaseModel, Field
from ayiti_ai.guardrails.lid.schema import PreprocessedText


class LevelResult(BaseModel):
    """Result returned by a single level of the LID system."""
    matched: bool
    language: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    evidence: dict = Field(default_factory=dict)


class LIDLevel(Protocol):
    """Protocol that all LID levels (Level 1, 2, 3) must implement."""
    
    @property
    def name(self) -> str:
        """Name of the level (e.g., 'Level 1: Rules')."""
        ...

    @property
    def version(self) -> str:
        """Semantic version of the level implementation."""
        ...

    def is_ready(self) -> bool:
        """Return True if the level is loaded and ready for inference."""
        ...

    def warmup(self) -> None:
        """Perform initialization or model loading tasks."""
        ...

    def predict(self, text: str, context: PreprocessedText) -> LevelResult:
        """Perform language identification for the given text and context."""
        ...
