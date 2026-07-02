"""
Tests unitaires pour les modules LoRA et modèle.

Ces tests vérifient la configuration LoRA sans charger le modèle complet
(trop lourd pour les tests unitaires).
"""

from unittest.mock import MagicMock, patch

import pytest


class TestGetLoraConfig:
    """Tests pour get_lora_config() dans lora_adapter.py."""

    def test_returns_lora_config(self):
        from ayiti_ai.models.lora_adapter import get_lora_config

        config = get_lora_config()
        assert config is not None

    def test_default_values(self):
        from ayiti_ai.models.lora_adapter import get_lora_config

        config = get_lora_config()
        assert config.r == 16
        assert config.lora_alpha == 32
        assert config.lora_dropout == 0.05

    def test_custom_r_value(self):
        from ayiti_ai.models.lora_adapter import get_lora_config

        config = get_lora_config(r=8)
        assert config.r == 8

    def test_custom_alpha(self):
        from ayiti_ai.models.lora_adapter import get_lora_config

        config = get_lora_config(alpha=64)
        assert config.lora_alpha == 64

    def test_custom_dropout(self):
        from ayiti_ai.models.lora_adapter import get_lora_config

        config = get_lora_config(dropout=0.1)
        assert config.lora_dropout == pytest.approx(0.1)

    def test_default_target_modules(self):
        from ayiti_ai.models.lora_adapter import get_lora_config

        config = get_lora_config()
        assert "q_proj" in config.target_modules
        assert "v_proj" in config.target_modules

    def test_custom_target_modules(self):
        from ayiti_ai.models.lora_adapter import get_lora_config

        modules = ["q_proj", "k_proj"]
        config = get_lora_config(target_modules=modules)
        assert set(config.target_modules) == set(modules)

    def test_task_type_causal_lm(self):
        from peft import TaskType

        from ayiti_ai.models.lora_adapter import get_lora_config

        config = get_lora_config()
        assert config.task_type == TaskType.CAUSAL_LM

    def test_bias_none(self):
        from ayiti_ai.models.lora_adapter import get_lora_config

        config = get_lora_config()
        assert config.bias == "none"


class TestApplyLoraFromYaml:
    """Tests pour apply_lora() — avec mock du modèle."""

    def test_apply_lora_calls_get_peft_model(self, tmp_path):
        """Vérifie que apply_lora appelle bien get_peft_model."""
        import yaml

        from ayiti_ai.models.lora_adapter import apply_lora

        # Créer un faux fichier YAML
        config_data = {
            "r": 16,
            "lora_alpha": 32,
            "lora_dropout": 0.05,
            "target_modules": ["q_proj", "v_proj"],
            "bias": "none",
            "task_type": "CAUSAL_LM",
        }
        config_path = tmp_path / "lora.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        mock_model = MagicMock()

        with patch("ayiti_ai.models.lora_adapter.get_peft_model") as mock_peft:
            mock_peft.return_value = mock_model
            apply_lora(mock_model, config_path=str(config_path))

        mock_peft.assert_called_once()

    def test_apply_lora_missing_config_raises(self):
        from ayiti_ai.models.lora_adapter import apply_lora

        mock_model = MagicMock()
        with pytest.raises(FileNotFoundError):
            apply_lora(mock_model, config_path="nonexistent_config.yaml")


class TestModelsImports:
    """Vérifie que tous les symboles publics sont correctement exportés."""

    def test_import_load_qwen_model_and_tokenizer(self):
        from ayiti_ai.models import load_qwen_model_and_tokenizer

        assert callable(load_qwen_model_and_tokenizer)

    def test_import_load_qwen_model_alias(self):
        from ayiti_ai.models import load_qwen_model

        assert callable(load_qwen_model)

    def test_import_apply_lora(self):
        from ayiti_ai.models import apply_lora

        assert callable(apply_lora)

    def test_import_get_lora_config(self):
        from ayiti_ai.models import get_lora_config

        assert callable(get_lora_config)
