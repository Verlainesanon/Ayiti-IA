# IA Haïtienne - Ayiti-AI

Projet de construction d'une IA multimodale souveraine pour Haïti.

## Structure
- `src/` : Code source principal
- `config/` : Configurations YAML
- `data/` : Datasets (ignorés par Git)
- `notebooks/` : Jupyter notebooks pour l'exploration
- `scripts/` : Scripts utilitaires
- `tests/` : Tests unitaires
- `docs/` : Documentation

## Installation
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Utilisation
Préparer les données : `make data`

Lancer les tests : `make test`
