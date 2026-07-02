"""
Tests unitaires pour AyitiDatasetBuilder.

Ces tests ne nécessitent pas de fichiers de données réels —
ils créent des données temporaires et vérifient le comportement.
"""
import json
import pytest
import tempfile
import os
from pathlib import Path

from src.data.dataset_builder import AyitiDatasetBuilder


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_RECORDS = [
    {
        "instruction": "Kijan ou rele?",
        "output": "Mwen rele Ayiti-AI, yon asistan entèlijan.",
        "language": "ht",
    },
    {
        "instruction": "Comment tu t'appelles?",
        "output": "Je m'appelle Ayiti-AI, un assistant intelligent.",
        "language": "fr",
    },
    {
        "instruction": "What is your name?",
        "output": "My name is Ayiti-AI, an intelligent assistant.",
        "language": "en",
    },
]


@pytest.fixture
def tmp_dirs(tmp_path):
    """Crée des répertoires temporaires pour raw/ et processed/."""
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"
    raw.mkdir()
    processed.mkdir()
    return raw, processed


@pytest.fixture
def sample_jsonl(tmp_dirs):
    """Crée un fichier JSONL de test dans raw/."""
    raw, _ = tmp_dirs
    jsonl_path = raw / "test_data.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for record in SAMPLE_RECORDS:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return jsonl_path


@pytest.fixture
def builder(tmp_dirs, sample_jsonl):
    """Instance de AyitiDatasetBuilder avec des données temporaires."""
    raw, processed = tmp_dirs
    return AyitiDatasetBuilder(raw_path=str(raw), processed_path=str(processed))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCleanText:
    def test_removes_control_characters(self):
        builder = AyitiDatasetBuilder.__new__(AyitiDatasetBuilder)
        result = builder.clean_text("hello\x00world\x07")
        assert "\x00" not in result
        assert "\x07" not in result

    def test_collapses_whitespace(self):
        builder = AyitiDatasetBuilder.__new__(AyitiDatasetBuilder)
        result = builder.clean_text("  bonjou   monde  ")
        assert result == "bonjou monde"

    def test_preserves_haitian_creole(self):
        builder = AyitiDatasetBuilder.__new__(AyitiDatasetBuilder)
        text = "Kijan ou rele? Mwen rele Ayiti."
        result = builder.clean_text(text)
        assert result == text

    def test_preserves_accented_characters(self):
        builder = AyitiDatasetBuilder.__new__(AyitiDatasetBuilder)
        text = "Haïti, île magnifique, têt chèche"
        result = builder.clean_text(text)
        assert "ï" in result
        assert "è" in result


class TestLoadRawFiles:
    def test_loads_jsonl_correctly(self, builder):
        data = builder.load_raw_files(pattern="*.jsonl")
        assert len(data) == len(SAMPLE_RECORDS)

    def test_returns_dicts(self, builder):
        data = builder.load_raw_files()
        assert all(isinstance(item, dict) for item in data)

    def test_empty_directory(self, tmp_dirs):
        raw, processed = tmp_dirs
        empty_builder = AyitiDatasetBuilder(
            raw_path=str(raw / "empty"),
            processed_path=str(processed),
        )
        Path(raw / "empty").mkdir()
        data = empty_builder.load_raw_files()
        assert data == []

    def test_required_keys_present(self, builder):
        data = builder.load_raw_files()
        for item in data:
            assert "instruction" in item
            assert "output" in item


class TestBuildTrainDataset:
    def test_returns_dataset(self, builder):
        from datasets import Dataset
        dataset = builder.build_train_dataset()
        assert isinstance(dataset, Dataset)

    def test_dataset_length(self, builder):
        dataset = builder.build_train_dataset()
        assert len(dataset) == len(SAMPLE_RECORDS)

    def test_parquet_file_created(self, builder, tmp_dirs):
        _, processed = tmp_dirs
        builder.build_train_dataset()
        parquet_file = processed / "ayiti_train.parquet"
        assert parquet_file.exists()

    def test_dataset_has_instruction_column(self, builder):
        dataset = builder.build_train_dataset()
        assert "instruction" in dataset.column_names

    def test_dataset_has_output_column(self, builder):
        dataset = builder.build_train_dataset()
        assert "output" in dataset.column_names


class TestBuildTokenizerCorpus:
    def test_creates_corpus_file(self, builder, tmp_dirs):
        _, processed = tmp_dirs
        corpus_path = builder.build_tokenizer_corpus()
        assert Path(corpus_path).exists()

    def test_corpus_contains_haitian_text(self, builder):
        corpus_path = builder.build_tokenizer_corpus()
        with open(corpus_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Kijan" in content or "rele" in content

    def test_corpus_not_empty(self, builder):
        corpus_path = builder.build_tokenizer_corpus()
        assert Path(corpus_path).stat().st_size > 0
