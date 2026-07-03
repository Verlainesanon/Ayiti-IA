from typing import Literal, Optional
from pydantic import BaseModel, Field


class LIDInput(BaseModel):
    """Input parameters for language detection."""
    text: str = Field(..., min_length=1, max_length=5000, description="The input text to analyze.")
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum confidence threshold.")
    return_alternatives: bool = Field(False, description="Whether to return secondary languages.")
    enable_levels: Optional[list[int]] = Field(None, description="Subset of levels (1, 2, 3) to enable.")


class LangScore(BaseModel):
    """Represents a language prediction with its confidence score."""
    language: str
    score: float = Field(..., ge=0.0, le=1.0)


class PreprocessedText(BaseModel):
    """Immutable representation of a preprocessed text."""
    original_text: str
    normalized_text: str
    char_count: int
    word_count: int
    script: str
    tokens: list[str]
    bigrams: list[str]
    trigrams: list[str]


class LIDResult(BaseModel):
    """The structured result returned by the RobustLID pipeline."""
    primary_language: Literal["ht", "fr", "en", "unknown"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    level_used: int = Field(..., ge=0, le=3)  # 0 = early exit (unknown)
    is_code_switched: bool
    secondary_languages: list[LangScore] = Field(default_factory=list)
    detected_markers: list[str] = Field(default_factory=list)
    latency_ms: float
    preprocessing_metadata: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    model_version: str
