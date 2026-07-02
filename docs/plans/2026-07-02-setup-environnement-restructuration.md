# Packaging & Restructuration Technique S1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructurer le code d'Ayiti-AI sous forme de package installable (`ayiti_ai`), configurer le packaging avec `pyproject.toml`, configurer `pre-commit` et `pre-commit-hooks` (ruff, mypy, bandit), initialiser DVC, et mettre en place le workflow CI GitHub Actions.

**Architecture:** Le code source sera migré de l'arborescence à plat (`src/*`) vers une structure de package modulaire (`src/ayiti_ai/*`). Le packaging passera de dépendances non figées dans `requirements.txt` à un `pyproject.toml` moderne déclarant un mode editable et des dépendances épinglées. Les linters et type checkers seront exécutés localement via `pre-commit` et automatiquement dans le cloud via GitHub Actions.

**Tech Stack:** Python 3.10+, Pytest, Ruff, Mypy, Bandit, DVC, GitHub Actions, Git.

---

### Task 1: Création de l'arborescence et test d'importation initial

**Files:**
- Create: `src/ayiti_ai/__init__.py`
- Create: `src/ayiti_ai/data/__init__.py`
- Create: `src/ayiti_ai/models/__init__.py`
- Create: `src/ayiti_ai/training/__init__.py`
- Create: `src/ayiti_ai/evaluation/__init__.py`
- Create: `src/ayiti_ai/inference/__init__.py`
- Create: `src/ayiti_ai/guardrails/__init__.py`
- Create: `src/ayiti_ai/rag/__init__.py`
- Create: `src/ayiti_ai/utils/__init__.py`
- Create: `tests/test_imports_new.py`

**Step 1: Write the failing test**

Créez le fichier `tests/test_imports_new.py` :
```python
import pytest

def test_imports_ayiti_ai():
    try:
        import ayiti_ai
        from ayiti_ai import data
        from ayiti_ai import models
        from ayiti_ai import training
        from ayiti_ai import evaluation
        from ayiti_ai import inference
        from ayiti_ai import guardrails
        from ayiti_ai import rag
        from ayiti_ai import utils
    except ImportError as e:
        pytest.fail(f"L'importation a échoué : {e}")
```

**Step 2: Run test to verify it fails**

Run: `.\venv\Scripts\pytest tests/test_imports_new.py -v`
Expected: FAIL avec `ModuleNotFoundError: No module named 'ayiti_ai'` (car le package n'existe pas encore et n'est pas dans le path).

**Step 3: Write minimal implementation**

Créez les dossiers et fichiers `__init__.py` vides :
- `src/ayiti_ai/__init__.py` contenant `__version__ = "0.1.0"`
- `src/ayiti_ai/data/__init__.py`
- `src/ayiti_ai/models/__init__.py`
- `src/ayiti_ai/training/__init__.py`
- `src/ayiti_ai/evaluation/__init__.py`
- `src/ayiti_ai/inference/__init__.py`
- `src/ayiti_ai/guardrails/__init__.py`
- `src/ayiti_ai/rag/__init__.py`
- `src/ayiti_ai/utils/__init__.py`

Ajoutez temporairement le chemin `src` au path Python de pytest dans `pytest.ini` ou via variable d'environnement pour ce test.
Créez `pytest.ini` à la racine :
```ini
[pytest]
pythonpath = src
```

**Step 4: Run test to verify it passes**

Run: `.\venv\Scripts\pytest tests/test_imports_new.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pytest.ini tests/test_imports_new.py src/ayiti_ai/
git commit -m "chore: setup new package structure and add initial import tests"
```

---

### Task 2: Configuration du Packaging avec `pyproject.toml`

**Files:**
- Create: `pyproject.toml`
- Modify: `src/ayiti_ai/__init__.py`

**Step 1: Write the failing test**

Modifiez `tests/test_imports_new.py` pour tester que le package est installé en mode editable de manière globale (sans dépendre de `pythonpath` dans `pytest.ini`). Supprimez temporairement `pytest.ini` pour tester.
Run: `.\venv\Scripts\pytest tests/test_imports_new.py -v`
Expected: FAIL avec `ModuleNotFoundError: No module named 'ayiti_ai'` (car `pytest.ini` est supprimé).

**Step 2: Write minimal implementation**

Restaurez `pytest.ini`. Créez le fichier `pyproject.toml` à la racine :
```toml
[build-system]
requires = ["setuptools>=61.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ayiti_ai"
version = "0.1.0"
description = "Sovereign Haitian Multimodal AI Platform"
readme = "README.md"
requires-python = ">=3.10"
authors = [
    { name = "Ayiti-AI Team" }
]
license = { text = "Apache-2.0" }
dependencies = [
    "torch>=2.1.0",
    "transformers>=4.36.0",
    "peft>=0.7.0",
    "trl>=0.7.0",
    "bitsandbytes>=0.41.0",
    "datasets>=2.14.0",
    "pandas>=2.0.0",
    "pyarrow>=14.0.0",
    "tokenizers>=0.15.0",
    "openpyxl>=3.1.0",
    "sacrebleu>=2.3.0",
    "rouge-score>=0.1.2",
    "pyyaml>=6.0",
    "tqdm>=4.65.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.9",
    "mypy>=1.8.0",
    "bandit>=1.7.5",
    "pre-commit>=3.5.0",
    "dvc[s3]>=3.30.0",
    "python-dotenv>=1.0.0"
]

[tool.setuptools.packages.find]
where = ["src"]
```

Installez le package en mode éditable avec les dépendances dev :
Run: `.\venv\Scripts\pip install -e ".[dev]"`

**Step 3: Run test to verify it passes**

Supprimez définitivement `pytest.ini` pour s'assurer que l'importation se fait par le biais de l'installation éditable globale.
Run: `.\venv\Scripts\pytest tests/test_imports_new.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git rm pytest.ini
git add pyproject.toml
git commit -m "feat: add pyproject.toml and install package in editable mode"
```

---

### Task 3: Migration des Fichiers et Mise à Jour des Imports

**Files:**
- Modify: Déplacer et renommer tous les fichiers du package.
  - Déplacer `src/data/dataset_builder.py` vers `src/ayiti_ai/data/builder.py`
  - Déplacer `src/models/qwen_loader.py` vers `src/ayiti_ai/models/qwen_loader.py`
  - Déplacer `src/models/lora_adapter.py` vers `src/ayiti_ai/models/lora_adapter.py`
  - Déplacer `src/models/__init__.py` vers `src/ayiti_ai/models/__init__.py`
  - Déplacer `src/training/trainer.py` vers `src/ayiti_ai/training/trainer.py`
  - Déplacer `src/inference/chat.py` vers `src/ayiti_ai/inference/chat.py`
  - Déplacer `src/evaluation/__init__.py` vers `src/ayiti_ai/evaluation/__init__.py`
  - Déplacer `src/evaluation/metrics.py` vers `src/ayiti_ai/evaluation/metrics.py`
  - Déplacer `src/__init__.py` vers `src/ayiti_ai/__init__.py`
- Modify: `tests/test_dataset_builder.py`
- Modify: `tests/test_lora_config.py`

**Step 1: Run tests to verify they fail**

Puisque les fichiers ont été déplacés sans mettre à jour les chemins d'importation dans les tests :
Run: `.\venv\Scripts\pytest tests/ -v`
Expected: FAIL sur `test_dataset_builder.py` et `test_lora_config.py` à cause de `ModuleNotFoundError` (les imports pointent vers l'ancien chemin `src.data` au lieu de `ayiti_ai.data`).

**Step 2: Update minimal implementation**

Mettez à jour les imports dans les tests et fichiers migrés :
- Dans `tests/test_dataset_builder.py` : remplacer `from src.data.dataset_builder import AyitiDatasetBuilder` par `from ayiti_ai.data.builder import AyitiDatasetBuilder`.
- Dans `tests/test_lora_config.py` : remplacer les imports de `src.models.*` par `ayiti_ai.models.*`.
- Dans `src/ayiti_ai/training/trainer.py` : remplacer les imports de `src.models.qwen_loader` par `ayiti_ai.models.qwen_loader`.
- Dans `src/ayiti_ai/evaluation/metrics.py` : remplacer `from src.inference.chat import AyitiChat` par `from ayiti_ai.inference.chat import AyitiChat`.

Supprimez les anciens dossiers vides sous `src/` (les sous-dossiers de premier niveau restés vides comme `src/data`, `src/models`, etc.).

**Step 3: Run tests to verify they pass**

Run: `.\venv\Scripts\pytest tests/ -v`
Expected: PASS (Tous les 31 tests d'origine + le test d'importation passent).

**Step 4: Commit**

```bash
git add src/ayiti_ai/ tests/
git commit -m "refactor: migrate all source files under src/ayiti_ai/ and update imports"
```

---

### Task 4: Intégration de pre-commit, Ruff et Mypy

**Files:**
- Create: `.pre-commit-config.yaml`
- Modify: `pyproject.toml`

**Step 1: Write the failing check**

Essayez d'exécuter pre-commit :
Run: `.\venv\Scripts\pre-commit run --all-files`
Expected: FAIL car aucun fichier `.pre-commit-config.yaml` n'est configuré.

**Step 2: Write minimal implementation**

Ajoutez la configuration de Ruff et Mypy dans `pyproject.toml` :
```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "W", "I", "B"]
ignore = []

[tool.mypy]
python_version = "3.10"
strict = true
warn_unused_configs = true
ignore_missing_imports = true
```

Créez `.pre-commit-config.yaml` à la racine :
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
        args: ['--maxkb=10000']

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [ --fix ]
      - id: ruff-format
```

Installez les hooks git :
Run: `.\venv\Scripts\pre-commit install`

**Step 3: Run checkers to verify they pass**

Run: `.\venv\Scripts\pre-commit run --all-files`
Expected: PASS (Les fichiers sont nettoyés et formatés).

**Step 4: Commit**

```bash
git add .pre-commit-config.yaml pyproject.toml
git commit -m "chore: add pre-commit hooks, ruff and mypy configuration"
```

---

### Task 5: Initialisation de DVC pour le Versionnage des Données

**Files:**
- Create: `.dvcignore`
- Modify: `.gitignore`

**Step 1: Write the failing check**

Vérifiez le statut DVC :
Run: `.\venv\Scripts\dvc status`
Expected: FAIL avec un message indiquant que le dépôt n'est pas un dépôt DVC.

**Step 2: Write minimal implementation**

Initialisez DVC :
Run: `.\venv\Scripts\dvc init`

Ajoutez les répertoires de données brutes et préparées à DVC :
Run: `.\venv\Scripts\dvc add data/raw/`
Run: `.\venv\Scripts\dvc add data/processed/`

Assurez-vous que `.gitignore` ignore les dossiers physiques de données mais suit les fichiers `.dvc` :
Ajoutez à la fin de `.gitignore` :
```
/data/raw/*
!/data/raw/.gitkeep
!/data/raw/*.dvc
/data/processed/*
!/data/processed/*.dvc
```

Configurez un local/remote temporaire si nécessaire (ou laissez à l'utilisateur de lier son remote).

**Step 3: Run check to verify it passes**

Run: `.\venv\Scripts\dvc status`
Expected: "Data and pipelines are up to date."

**Step 4: Commit**

```bash
git add .dvc/ .dvcignore data/raw.dvc data/processed.dvc .gitignore
git commit -m "chore: initialize dvc and track raw/processed data directories"
```

---

### Task 6: Configuration de GitHub Actions (Workflow CI)

**Files:**
- Create: `.github/workflows/ci.yml`

**Step 1: Write the failing check**

Un test local simple pour s'assurer que le fichier YAML du workflow est syntaxiquement correct :
Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`
Expected: FileNotFoundError (car le fichier n'existe pas encore).

**Step 2: Write minimal implementation**

Créez le fichier `.github/workflows/ci.yml` :
```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint with Ruff
        run: |
          ruff check .
          ruff format --check .

      - name: Test with pytest
        run: |
          pytest tests/ -v --cov=src/ayiti_ai --cov-report=xml
```

**Step 3: Run check to verify it passes**

Vérifiez la validité syntaxique :
Run: `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"`
Expected: Pas de levée d'exception (PASS).

**Step 4: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: configure github actions workflow for linting and testing"
```
