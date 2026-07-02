# Findings & Decisions

## Requirements
- Restructurer le projet dans un package `ayiti_ai`.
- Mettre en place `pyproject.toml` avec typage strict et linting.
- Intégrer DVC pour le versioning des données.
- Intégrer les pre-commit hooks.
- Configurer les GitHub Actions.
- Conserver 100% de passage sur la suite de tests existante (31/31).

## Research Findings
- Les scripts d'entraînement, d'évaluation et de chat importent directement de `src.models`, `src.data`, `src.training`, etc. Ces imports devront être redirigés vers `src.ayiti_ai.models`, etc.
- Le fichier `requirements.txt` contient 26 lignes de dépendances à migrer dans `pyproject.toml`.

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Package local `ayiti_ai` | Structure propre, isole le code de l'application principale |
| Utilisation de Ruff | Linter et formateur extrêmement rapide |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
|       |            |

## Resources
- Plan d'environnement : [01_ENVIRONNEMENT_ET_SETUP.md](file:///c:/Users/User/Documents/Glip/Ayiti IA/Plan/01_ENVIRONNEMENT_ET_SETUP.md)
- Roadmap détaillée : [11_ROADMAP_12_SEMAINES.md](file:///c:/Users/User/Documents/Glip/Ayiti IA/Plan/11_ROADMAP_12_SEMAINES.md)

## Visual/Browser Findings
- Aucun pour le moment.
