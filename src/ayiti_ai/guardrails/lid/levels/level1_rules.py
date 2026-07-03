import os
import yaml
from typing import Any, Optional
from ayiti_ai.guardrails.lid.levels.base import LevelResult, LIDLevel
from ayiti_ai.guardrails.lid.schema import PreprocessedText
from ayiti_ai.guardrails.lid.exceptions import LIDConfigError


class Level1Rules(LIDLevel):
    """Level 1 of the LID system: Deterministic rules based on linguistic markers."""

    def __init__(
        self,
        markers_config_path: str = "config/lid_markers.yaml",
        activation_threshold: float = 0.85,
        disambiguation_gap: float = 0.4,
        ngram_bonus: float = 0.5,
    ):
        self.config_path = markers_config_path
        self.activation_threshold = activation_threshold
        self.disambiguation_gap = disambiguation_gap
        self.ngram_bonus = ngram_bonus
        
        # In-memory structured representation of markers
        # Map: language -> set of words
        self.words: dict[str, dict[str, float]] = {"ht": {}, "fr": {}, "en": {}}
        # Map: language -> list of (pattern, confidence)
        self.ngrams: dict[str, list[tuple[str, float]]] = {"ht": [], "fr": [], "en": {}}
        # Map: language -> list of (char, confidence)
        self.diacritics: dict[str, list[tuple[str, float]]] = {"ht": [], "fr": [], "en": {}}
        # Map: language -> list of (pattern, confidence)
        self.contractions: dict[str, list[tuple[str, float]]] = {"ht": [], "fr": [], "en": {}}
        
        self._is_ready = False

    @property
    def name(self) -> str:
        return "Level 1: Rules"

    @property
    def version(self) -> str:
        return "1.0.0"

    def is_ready(self) -> bool:
        return self._is_ready

    def warmup(self) -> None:
        """Load and compile markers from the YAML configuration file."""
        if not os.path.exists(self.config_path):
            raise LIDConfigError(f"Markers configuration not found: {self.config_path}")
            
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                
            markers_data = data.get("markers", {})
            for lang in ["ht", "fr", "en"]:
                lang_data = markers_data.get(lang, {})
                
                # 1. Load words (tma_particles, pronouns, verbs, verbs_conjugated, lexical)
                word_sections = ["tma_particles", "pronouns", "verbs", "verbs_conjugated", "lexical"]
                for section in word_sections:
                    for item in lang_data.get(section, []):
                        word = item.get("word")
                        conf = item.get("confidence", 1.0)
                        if word:
                            self.words[lang][word.lower()] = conf
                            # Also add variants as separate lookups
                            for variant in item.get("variants", []):
                                self.words[lang][variant.strip().lower()] = conf
                
                # 2. Load ngrams
                for item in lang_data.get("ngrams", []):
                    pattern = item.get("pattern")
                    conf = item.get("confidence", 1.0)
                    if pattern:
                        self.ngrams[lang].append((pattern.lower(), conf))
                        
                # 3. Load contractions (used for fr)
                for item in lang_data.get("contractions", []):
                    pattern = item.get("pattern")
                    conf = item.get("confidence", 1.0)
                    if pattern:
                        self.contractions[lang].append((pattern.lower(), conf))
                        
                # 4. Load diacritics
                for item in lang_data.get("diacritics", []):
                    char = item.get("char")
                    conf = item.get("confidence", 1.0)
                    if char:
                        self.diacritics[lang].append((char, conf))
            
            self._is_ready = True
        except Exception as e:
            raise LIDConfigError(f"Failed to load markers config from {self.config_path}: {e}") from e

    def predict(self, text: str, context: PreprocessedText) -> LevelResult:
        """Run the rule-based language identification algorithm."""
        if not self.is_ready():
            self.warmup()
            
        scores = {"ht": 0.0, "fr": 0.0, "en": 0.0}
        matched_markers = {"ht": [], "fr": [], "en": []}
        
        normalized_lower = context.normalized_text.lower()
        
        for lang in ["ht", "fr", "en"]:
            # 1. Match word tokens
            for token in context.tokens:
                if token in self.words[lang]:
                    conf = self.words[lang][token]
                    scores[lang] += conf
                    matched_markers[lang].append(token)
            
            # 2. Match n-grams
            for pattern, conf in self.ngrams[lang]:
                if pattern in context.bigrams or pattern in context.trigrams:
                    scores[lang] += conf
                    # For HT, apply an extra bonus for TMA ngrams
                    if lang == "ht":
                        scores[lang] += self.ngram_bonus
                    matched_markers[lang].append(pattern)
            
            # 3. Match contractions (substring search)
            for pattern, conf in self.contractions[lang]:
                if pattern in normalized_lower:
                    scores[lang] += conf
                    matched_markers[lang].append(pattern)
                    
            # 4. Match diacritics (char search)
            for char, conf in self.diacritics[lang]:
                if char in context.normalized_text:
                    scores[lang] += conf
                    matched_markers[lang].append(char)
                    
        # Find best and second best languages
        sorted_langs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        best_lang, best_score = sorted_langs[0]
        second_lang, second_score = sorted_langs[1]
        
        # Decision Logic
        if best_score == 0:
            return LevelResult(matched=False, evidence={"scores": scores})
            
        gap = best_score - second_score
        
        if best_score >= self.activation_threshold and gap >= self.disambiguation_gap:
            return LevelResult(
                matched=True,
                language=best_lang,
                confidence=1.0, # Rules are deterministic (1.0 confidence when matched)
                evidence={
                    "scores": scores,
                    "matched_markers": matched_markers[best_lang]
                }
            )
            
        return LevelResult(
            matched=False,
            evidence={
                "reason": "ambiguous or below threshold",
                "scores": scores,
                "best_candidate": best_lang,
                "gap": gap
            }
        )
