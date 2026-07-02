# Walkthrough — Phase 1 : Fondations & Packaging Ayiti-AI

## Ce qui a été accompli

### 1. Package `ayiti_ai` installable

Le projet est passé d'une structure à plat (`src/models/`, `src/data/`…) à un **package Python moderne** :

```
src/ayiti_ai/
├── __init__.py          ← __version__ = "0.1.0", lazy imports
├── data/
│   ├── __init__.py
│   └── builder.py       ← AyitiDatasetBuilder migré
├── models/
│   ├── __init__.py      ← lazy __getattr__ (évite de charger torch au import)
│   ├── qwen_loader.py   ← migré + type hints
│   └── lora_adapter.py  ← migré + type hints
├── training/__init__.py
├── evaluation/
│   ├── __init__.py
│   └── metrics.py       ← migré (BLEU, ROUGE, perplexité, evaluate_model)
├── inference/
│   ├── __init__.py
│   └── chat.py          ← AyitiChat migré (generate, chat_loop, main CLI)
├── guardrails/__init__.py
├── rag/__init__.py
└── utils/__init__.py
```

Installé en mode éditable : `pip install -e .` → `import ayiti_ai` ✅

---

### 2. `pyproject.toml` complet

- **Build** : `setuptools>=68`, packages découverts dans `src/`
- **Dépendances** : torch, transformers, peft, trl, datasets, sacrebleu, rouge-score…
- **Entry points CLI** : `ayiti-train`, `ayiti-chat`, `ayiti-eval`
- **Config Ruff** : lint + format, target Python 3.10
- **Config Mypy** : `ignore_missing_imports=true` (à renforcer en Phase 2)
- **Config Pytest** : `pythonpath = ["src"]`, `testpaths = ["tests"]`

---

### 3. Tests : 41/41 PASS ✅

| Suite | Tests | Résultat |
|-------|-------|----------|
| `test_dataset_builder.py` | 16 | ✅ PASS |
| `test_lora_config.py` | 15 | ✅ PASS |
| `test_package_imports.py` | 10 | ✅ PASS (nouveaux) |
| **Total** | **41** | **100%** |

---

### 4. Outillage DevOps

| Fichier | Rôle |
|---------|------|
| [.pre-commit-config.yaml](file:///c:/Users/User/Documents/Glip/Ayiti%20IA/.pre-commit-config.yaml) | Ruff lint+format, trailing-whitespace, check-yaml, gitleaks |
| [.github/workflows/ci.yml](file:///c:/Users/User/Documents/Glip/Ayiti%20IA/.github/workflows/ci.yml) | 4 jobs : lint → test (py3.10+3.11) → mypy → bandit |
| [.env.example](file:///c:/Users/User/Documents/Glip/Ayiti%20IA/.env.example) | Template HF_TOKEN, WANDB, Argilla, AWS |

---

### 5. DVC — Versionnage des données

```
dvc init
dvc add data/raw data/processed
# → data/raw.dvc + data/processed.dvc commitées
# → data/ retirée de Git
dvc status → "Data and pipelines are up to date."
```

---

## Commits produits

| SHA | Message |
|-----|---------|
| `51b12c1` | feat(package): Phase 1 — restructuration en src/ayiti_ai/ + packaging |
| `79a14b2` | chore(dvc): init DVC data versioning |

---

## Prochaine étape — Phase 2 : Pipeline de données

Objectifs Phase 2 :
1. **Collecte** : scraping Wikipedia créole + Fonkoze + Bibliothèque nationale
2. **Qualité** : intégration Argilla pour annotation et review humaine
3. **Format** : conversion en format ChatML instruction/output
4. **Entraînement SFT** : premier run Qwen2.5-1.5B avec LoRA sur Colab
5. **Métriques** : BLEU/ROUGE sur validation set haïtien
