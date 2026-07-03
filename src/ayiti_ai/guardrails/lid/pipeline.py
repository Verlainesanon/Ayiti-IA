"""
RobustLID — The main 3-level Language Identification Pipeline.

Architecture (Pyramid of Robustness):
  Level 1: Deterministic rules (< 0.5 ms)  — Linguistic markers
  Level 2: FastText lid.176.ftz (1-2 ms)   — Statistical model  
  Level 3: CharCNN (3-5 ms)                — Neural on characters [TODO S3]

Usage:
    from ayiti_ai.guardrails.lid.pipeline import RobustLID
    
    lid = RobustLID()
    lid.warmup()
    result = lid.detect("Mwen ap manje nan lakou a.")
    print(result.primary_language)  # "ht"
"""

import logging
import time
from typing import Optional

from ayiti_ai.guardrails.lid.schema import LIDInput, LIDResult, LangScore, PreprocessedText
from ayiti_ai.guardrails.lid.preprocessing import preprocess_text, detect_script
from ayiti_ai.guardrails.lid.levels.base import LIDLevel
from ayiti_ai.guardrails.lid.levels.level1_rules import Level1Rules
from ayiti_ai.guardrails.lid.levels.level2_fasttext import Level2FastText
from ayiti_ai.guardrails.lid.exceptions import LIDInvalidInputError, LIDInferenceError

logger = logging.getLogger(__name__)

MODEL_VERSION = "1.0.0"


class RobustLID:
    """
    Orchestrates the 3-level Language Identification pyramid.
    Fail-safe: if a level crashes, the next level is tried.
    """

    def __init__(
        self,
        markers_config_path: str = "config/lid_markers.yaml",
        fasttext_model_path: str = "models/lid.176.ftz",
        enable_cache: bool = True,
        min_text_length: int = 2,
        max_text_length: int = 5000,
        code_switch_threshold: float = 0.30,
    ):
        self.min_text_length = min_text_length
        self.max_text_length = max_text_length
        self.code_switch_threshold = code_switch_threshold
        self.enable_cache = enable_cache
        self._cache: dict = {}

        # Initialize levels
        self._level1 = Level1Rules(markers_config_path=markers_config_path)
        self._level2 = Level2FastText(model_path=fasttext_model_path)
        # Level 3 (CharCNN) — placeholder until S3
        self._level3 = None

        self._levels: list[LIDLevel] = [self._level1, self._level2]
        self._ready = False

    def warmup(self) -> None:
        """Load all available levels. Level 3 is skipped if not implemented."""
        logger.info("Warming up RobustLID pipeline...")
        for level in self._levels:
            try:
                level.warmup()
                logger.info(f"[OK] {level.name} ready.")
            except Exception as e:
                logger.warning(f"[WARN] {level.name} failed to load: {e} — will skip.")
        self._ready = True
        logger.info("RobustLID pipeline warmed up.")

    def detect(self, text: str) -> LIDResult:
        """
        Run the full LID pipeline on the given text.
        Returns a LIDResult with language, confidence, level_used, and metadata.
        """
        t_start = time.perf_counter()

        # --- Input Validation ---
        if not isinstance(text, str) or len(text) < self.min_text_length:
            raise LIDInvalidInputError(
                f"Input text must be a string with at least {self.min_text_length} characters."
            )
        if len(text) > self.max_text_length:
            raise LIDInvalidInputError(
                f"Input text exceeds maximum length of {self.max_text_length} characters."
            )

        # --- Cache check ---
        cache_key = hash(text)
        if self.enable_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # --- Preprocessing ---
        context = preprocess_text(text)
        warnings: list[str] = []

        # --- Early exits ---
        if context.script == "non-latin":
            warnings.append("non_latin_script_detected")
            return self._build_unknown_result(t_start, warnings)

        if context.word_count == 0:
            warnings.append("no_words_detected")
            return self._build_unknown_result(t_start, warnings)

        if context.word_count < 3:
            warnings.append("very_short_text")

        # --- Run levels sequentially ---
        best_candidate: Optional[dict] = None

        for i, level in enumerate(self._levels, start=1):
            if not level.is_ready():
                logger.debug(f"Skipping {level.name} (not ready).")
                continue

            try:
                level_result = level.predict(context.normalized_text, context)

                if level_result.matched and level_result.language:
                    latency_ms = (time.perf_counter() - t_start) * 1000
                    secondary = self._build_secondary_languages(
                        level_result.evidence, level_result.language
                    )
                    is_code_switched = self._detect_code_switching(secondary)
                    markers = level_result.evidence.get("matched_markers", [])

                    result = LIDResult(
                        primary_language=level_result.language,  # type: ignore[arg-type]
                        confidence=level_result.confidence or 0.0,
                        level_used=i,
                        is_code_switched=is_code_switched,
                        secondary_languages=secondary,
                        detected_markers=markers,
                        latency_ms=round(latency_ms, 3),
                        preprocessing_metadata={
                            "char_count": context.char_count,
                            "word_count": context.word_count,
                            "script": context.script,
                        },
                        warnings=warnings,
                        model_version=MODEL_VERSION,
                    )

                    if self.enable_cache:
                        self._cache[cache_key] = result

                    return result

                # Save best candidate in case no level fully matches
                if best_candidate is None and level_result.evidence.get("best_candidate"):
                    best_candidate = {
                        "language": level_result.evidence["best_candidate"],
                        "confidence": level_result.evidence.get("confidence", 0.0),
                        "level": i,
                    }

            except Exception as e:
                logger.error(f"Level {i} ({level.name}) crashed: {e}", exc_info=True)
                warnings.append(f"level_{i}_error")

        # --- Fallback: return best candidate with low confidence warning ---
        if best_candidate:
            warnings.append("low_confidence_fallback")
            latency_ms = (time.perf_counter() - t_start) * 1000
            return LIDResult(
                primary_language=best_candidate["language"],  # type: ignore[arg-type]
                confidence=best_candidate["confidence"],
                level_used=best_candidate["level"],
                is_code_switched=False,
                secondary_languages=[],
                detected_markers=[],
                latency_ms=round(latency_ms, 3),
                preprocessing_metadata={
                    "char_count": context.char_count,
                    "word_count": context.word_count,
                    "script": context.script,
                },
                warnings=warnings,
                model_version=MODEL_VERSION,
            )

        return self._build_unknown_result(t_start, warnings)

    def _build_unknown_result(self, t_start: float, warnings: list[str]) -> LIDResult:
        latency_ms = (time.perf_counter() - t_start) * 1000
        return LIDResult(
            primary_language="unknown",
            confidence=0.0,
            level_used=0,
            is_code_switched=False,
            secondary_languages=[],
            detected_markers=[],
            latency_ms=round(latency_ms, 3),
            preprocessing_metadata={},
            warnings=warnings,
            model_version=MODEL_VERSION,
        )

    def _build_secondary_languages(
        self, evidence: dict, primary: str
    ) -> list[LangScore]:
        """Extract secondary language scores from level evidence."""
        scores = evidence.get("normalized_predictions", {})
        if not scores:
            return []
        return [
            LangScore(language=lang, score=round(score, 4))
            for lang, score in scores.items()
            if lang != primary
        ]

    def _detect_code_switching(self, secondary: list[LangScore]) -> bool:
        """Return True if any secondary language score crosses the threshold."""
        return any(ls.score >= self.code_switch_threshold for ls in secondary)
