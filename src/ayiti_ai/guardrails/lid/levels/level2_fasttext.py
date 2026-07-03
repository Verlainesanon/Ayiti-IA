import os
from typing import Optional
from ayiti_ai.guardrails.lid.levels.base import LevelResult, LIDLevel
from ayiti_ai.guardrails.lid.schema import PreprocessedText
from ayiti_ai.guardrails.lid.exceptions import LIDModelLoadError, LIDInferenceError


class Level2FastText(LIDLevel):
    """Level 2 of the LID system: Statistical model using Facebook AI FastText."""

    def __init__(
        self,
        model_path: str = "models/lid.176.ftz",
        top_k: int = 5,
        min_confidence: float = 0.40,  # lowered for .ftz compressed model
        min_gap: float = 0.10,          # lowered for .ftz model
        languages_of_interest: Optional[list[str]] = None,
    ):
        self.model_path = model_path
        self.top_k = top_k
        self.min_confidence = min_confidence
        self.min_gap = min_gap
        self.languages_of_interest = languages_of_interest or ["ht", "fr", "en"]
        self.model = None
        self._is_ready = False

    @property
    def name(self) -> str:
        return "Level 2: FastText"

    @property
    def version(self) -> str:
        return "1.0.0"

    def is_ready(self) -> bool:
        return self._is_ready

    def warmup(self) -> None:
        """Load the fastText model into memory."""
        if not os.path.exists(self.model_path):
            raise LIDModelLoadError(f"FastText model file not found: {self.model_path}")
            
        try:
            import fasttext
            # Load model (prediction-only via fasttext-predict)
            self.model = fasttext.load_model(self.model_path)
            self._is_ready = True
        except Exception as e:
            raise LIDModelLoadError(f"Failed to load FastText model from {self.model_path}: {e}") from e

    def predict(self, text: str, context: PreprocessedText) -> LevelResult:
        """Predict the language using the FastText model."""
        if not self.is_ready():
            self.warmup()
            
        if not text.strip():
            return LevelResult(matched=False, evidence={"reason": "empty text"})

        # Clean newlines as fastText treats them as document boundaries
        cleaned_text = text.replace("\n", " ").strip()
        
        try:
            # Predict top-k classes
            labels, scores = self.model.predict(cleaned_text, k=self.top_k)
            
            # Map raw labels (e.g. '__label__ht') and raw scores into a dict
            raw_preds = {}
            for label, score in zip(labels, scores):
                clean_lang = label.replace("__label__", "")
                raw_preds[clean_lang] = float(score)
                
            # Filter by languages of interest
            filtered_preds = {
                lang: score for lang, score in raw_preds.items() 
                if lang in self.languages_of_interest
            }
            
            if not filtered_preds:
                return LevelResult(
                    matched=False, 
                    evidence={"reason": "no languages of interest matched", "raw_predictions": raw_preds}
                )
                
            # Re-normalize scores
            total_filtered_score = sum(filtered_preds.values())
            if total_filtered_score > 0:
                normalized_preds = {
                    lang: score / total_filtered_score 
                    for lang, score in filtered_preds.items()
                }
            else:
                normalized_preds = {lang: 0.0 for lang in filtered_preds}
                
            # Sort by normalized score
            sorted_normalized = sorted(normalized_preds.items(), key=lambda item: item[1], reverse=True)
            best_lang, best_score = sorted_normalized[0]
            
            if len(sorted_normalized) > 1:
                second_lang, second_score = sorted_normalized[1]
            else:
                second_score = 0.0
                
            gap = best_score - second_score
            
            evidence = {
                "raw_predictions": raw_preds,
                "normalized_predictions": normalized_preds,
                "best_candidate": best_lang,
                "confidence": best_score,
                "gap": gap
            }
            
            # Check thresholds
            if best_score >= self.min_confidence and gap >= self.min_gap:
                return LevelResult(
                    matched=True,
                    language=best_lang,
                    confidence=best_score,
                    evidence=evidence
                )
                
            return LevelResult(
                matched=False,
                evidence={
                    "reason": "below confidence or gap threshold",
                    **evidence
                }
            )
            
        except Exception as e:
            raise LIDInferenceError(f"FastText inference failed: {e}") from e
