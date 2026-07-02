.PHONY: help install data test train inference lint clean

help:
	@echo "Commandes disponibles — Ayiti-AI"
	@echo "  make install     - Installe les dépendances"
	@echo "  make data        - Prépare les datasets (raw → processed)"
	@echo "  make validate    - Valide les fichiers JSONL dans data/raw/"
	@echo "  make test        - Lance les tests unitaires"
	@echo "  make train       - Lance l'entraînement SFT (config par défaut)"
	@echo "  make inference   - Lance l'interface de chat interactive"
	@echo "  make lint        - Vérifie la syntaxe Python (pyflakes)"
	@echo "  make clean       - Nettoie les fichiers temporaires"

install:
	pip install -r requirements.txt

data:
	python -m src.data.dataset_builder

validate:
	python scripts/collect_data.py --action validate --file data/raw/seed_ht.jsonl

test:
	pytest tests/ -v

train:
	python scripts/run_training.py \
		--config config/training_config.yaml \
		--train_file data/raw/seed_ht.jsonl \
		--output_dir results/ayiti_lora

inference:
	python -m src.inference.chat --lang ht

lint:
	python -m pyflakes src/ scripts/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
