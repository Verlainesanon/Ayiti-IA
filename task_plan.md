# Task Plan: Restructuration Technique & Fondations (Phase 1)

## Goal
Restructurer le code d'Ayiti-AI sous forme de package installable (`ayiti_ai`), configurer le packaging avec `pyproject.toml`, mettre en place la CI, DVC pour les données, et valider le tout par des tests unitaires robustes.

## Current Phase
Phase 1: Requirements & Discovery

## Phases

### Phase 1: Requirements & Discovery
- [x] Analyser la structure actuelle du dépôt et des plans
- [x] Identifier les skills locaux et les règles de planification
- [x] Définir le périmètre de la restructuration
- **Status:** complete

### Phase 2: Planning & Structure
- [ ] Rédiger l'implementation plan complet sous `docs/plans/` au format TDD
- [ ] Valider l'approche technique avec l'utilisateur
- **Status:** in_progress

### Phase 3: Ingrédients Fondations & Packaging
- [ ] Créer la nouvelle structure de dossiers (`src/ayiti_ai/`)
- [ ] Rédiger `pyproject.toml`
- [ ] Installer le package localement en mode editable (`pip install -e ".[dev]"`)
- **Status:** pending

### Phase 4: Migration & Refactoring du Code
- [ ] Migrer le code existant et adapter les imports
- [ ] Mettre en place `.env.example` et configurer le chargement des variables d'environnement
- [ ] Configurer `pre-commit` et configurer les linters/type checkers (`ruff`, `mypy`)
- **Status:** pending

### Phase 5: Versioning des Données (DVC)
- [ ] Initialiser DVC
- [ ] Configurer un remote temporaire/final
- **Status:** pending

### Phase 6: CI & Tests de Validation
- [ ] Créer le workflow GitHub Actions `ci.yml`
- [ ] Lancer la suite complète de tests `pytest` et vérifier que tout est vert
- **Status:** pending

## Key Questions
1. Quelle est la version exacte de Python requise ? (Python 3.10 ou 3.11+ recommandé, nous utiliserons `python>=3.10` dans `pyproject.toml`).
2. Quelles dépendances doivent être épinglées exactement ? (Celles de `requirements.txt` avec des versions exactes).

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Utilisation de `pyproject.toml` | Standard moderne de packaging PEP 518/621 |
| Package nommé `ayiti_ai` | Standard PEP 8, évite les conflits d'imports |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
|       | 1       |            |
