import os
from typing import Optional
import yaml
from pydantic import BaseModel, Field
from ayiti_ai.guardrails.lid.exceptions import LIDConfigError


class PipelineConfig(BaseModel):
    min_text_length: int = 2
    max_text_length: int = 5000
    enable_cache: bool = True
    cache_size: int = 1000
    cache_ttl_seconds: int = 3600
    enabled_levels: list[int] = Field(default_factory=lambda: [1, 2, 3])


class PreprocessingConfig(BaseModel):
    unicode_normalization: str = "NFC"
    strip_urls: bool = True
    strip_emojis: bool = True
    lowercase_for_matching: bool = True
    keep_original: bool = True


class Level1RulesConfig(BaseModel):
    enabled: bool = True
    markers_config: str = "config/lid_markers.yaml"
    min_markers_for_match: int = 1
    weighted_scoring: bool = True
    ngram_bonus: float = 0.5
    activation_threshold: float = 0.85
    disambiguation_gap: float = 0.4


class Level2FastTextConfig(BaseModel):
    enabled: bool = True
    model_path: str = "models/lid.176.bin"
    top_k: int = 3
    min_confidence: float = 0.80
    languages_of_interest: list[str] = Field(default_factory=lambda: ["ht", "fr", "en"])
    fallback_language: Optional[str] = None


class Level3CharCNNConfig(BaseModel):
    enabled: bool = True
    model_path: str = "models/char_lid.pth"
    vocab_path: str = "models/char_vocab.json"
    min_confidence: float = 0.60
    max_seq_len: int = 128
    device: str = "cpu"
    batch_inference: bool = False


class CalibrationConfig(BaseModel):
    level_1: float = 1.0
    level_2: float = 0.95
    level_3: float = 0.85


class PostprocessingConfig(BaseModel):
    code_switch_threshold: float = 0.30
    calibration: CalibrationConfig = Field(default_factory=CalibrationConfig)


class MonitoringConfig(BaseModel):
    enable_prometheus: bool = True
    enable_structured_logs: bool = True
    log_predictions_sample_rate: float = 0.1


class LIDConfig(BaseModel):
    version: str = "1.0.0"
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    preprocessing: PreprocessingConfig = Field(default_factory=PreprocessingConfig)
    level_1_rules: Level1RulesConfig = Field(default_factory=Level1RulesConfig)
    level_2_fasttext: Level2FastTextConfig = Field(default_factory=Level2FastTextConfig)
    level_3_charcnn: Level3CharCNNConfig = Field(default_factory=Level3CharCNNConfig)
    postprocessing: PostprocessingConfig = Field(default_factory=PostprocessingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)


def load_config(config_path: str = "config/lid_config.yaml") -> LIDConfig:
    """Load and validate the general LID configuration file."""
    if not os.path.exists(config_path):
        raise LIDConfigError(f"Configuration file not found: {config_path}")
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        if data is None:
            return LIDConfig()
            
        return LIDConfig.model_validate(data)
    except Exception as e:
        raise LIDConfigError(f"Failed to load or validate config from {config_path}: {e}") from e
