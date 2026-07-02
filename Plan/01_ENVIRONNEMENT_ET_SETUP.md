# 01 — ENVIRONNEMENT & SETUP (FONDATIONS TECHNIQUES)

> **Objectif** : Avoir un environnement de développement reproductible, testable en CI, et sécurisé.
> **Durée estimée** : 3 à 5 jours de travail effectif.
> **Definition of Done** : Un `git clone` suivi de `make setup && make test` doit fonctionner sur n'importe quelle machine (Dell CPU, Colab GPU, serveur Linux).

---

## 1.1 STRUCTURE FINALE DU REPO (à atteindre)

Ne travaille pas avec la structure actuelle. Refactore vers ceci :

```
ayiti-ai/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # tests + lint sur chaque PR
│   │   ├── data-validation.yml       # valide les datasets sur push
│   │   └── release.yml               # build & publish sur tag
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── config/
│   ├── training_config.yaml
│   ├── lora_config.yaml
│   ├── inference_config.yaml
│   ├── eval_config.yaml
│   └── guardrails.yaml
├── data/
│   ├── raw/                          # jamais committé (DVC)
│   ├── processed/                    # jamais committé (DVC)
│   ├── external/                     # sources externes citées
│   └── README.md                     # taxonomie des catégories
├── docs/
│   ├── adr/                          # Architecture Decision Records
│   ├── stakeholders.md
│   ├── data-card.md                  # HuggingFace Datacard
│   └── model-card.md                 # HuggingFace Modelcard
├── notebooks/
│   ├── 01_eda.ipynb                  # exploration données
│   ├── 02_train_colab.ipynb
│   └── 03_error_analysis.ipynb
├── scripts/
│   ├── collect_data.py
│   ├── run_training.py
│   ├── run_evaluation.py
│   ├── run_red_team.py
│   └── export_model.py
├── src/
│   └── ayiti_ai/                     # ← package installable
│       ├── __init__.py
│       ├── data/
│       ├── models/
│       ├── training/
│       ├── evaluation/
│       ├── inference/
│       ├── guardrails/
│       ├── rag/
│       └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── deployment/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── k8s/                          # si Kubernetes
├── .env.example
├── .gitignore
├── .dockerignore
├── .pre-commit-config.yaml
├── .dvcignore
├── pyproject.toml                    # ← remplace setup.py
├── Makefile
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── SECURITY.md
```

**Action** : Crée cette arborescence complète cette semaine, même vide. C'est le squelette.

---

## 1.2 PACKAGING PROPRE (pyproject.toml)

Remplace `requirements.txt` seul par un **package installable**. Crée `pyproject.toml` avec :

- Métadonnées du projet (nom, version, auteurs, licence)
- Dépendances **pinnées** (versions exactes, pas `>=`)
- Dépendances de dev séparées (`[project.optional-dependencies]`)
- Entry points CLI (`ayiti-train`, `ayiti-chat`, `ayiti-eval`)
- Configuration `ruff`, `black`, `pytest`, `mypy`

**Definition of Done** : `pip install -e ".[dev]"` installe tout, et les CLI fonctionnent globalement.

---

## 1.3 GESTION DES SECRETS

**Interdit** : mettre des clés API, tokens HF, mots de passe dans le code ou Git.

Mets en place :
1. Un fichier `.env.example` versionné avec les **noms** des variables (valeurs vides).
2. Un fichier `.env` **ignoré par Git** avec les vraies valeurs.
3. Utilise `python-dotenv` ou `pydantic-settings` pour charger.
4. Installe `git-secrets` ou `gitleaks` en pre-commit hook pour détecter les fuites.
5. Sur GitHub : configure les **Secrets du repo** pour la CI (`HF_TOKEN`, `WANDB_API_KEY`, etc.).

Variables à prévoir :
```
HF_TOKEN=
WANDB_API_KEY=
OPENAI_API_KEY=          # pour évaluation LLM-as-judge
HUGGINGFACE_HUB_CACHE=
DATA_ENCRYPTION_KEY=     # si tu chiffres les données brutes
```

---

## 1.4 VERSIONING DES DONNÉES (DVC)

Les datasets sont **trop lourds pour Git**. Utilise **DVC** (Data Version Control) :

1. `pip install dvc dvc-s3` (ou `dvc-gdrive` si tu n'as pas d'S3).
2. `dvc init` à la racine.
3. `dvc add data/raw/` et `dvc add data/processed/`.
4. Configure un remote (S3, Backblaze B2, Google Drive, ou un serveur SSH que tu contrôles).
5. `.gitignore` doit contenir `/data/raw/*` et `/data/processed/*` sauf les `.dvc`.
6. Chaque changement de dataset → `dvc commit` + `git commit` du `.dvc`.

**Pourquoi c'est critique** : reproductibilité des expériences. Si tu ne peux pas rejouer un entraînement à l'identique 6 mois plus tard, ton projet n'est pas sérieux.

**Alternative allégée** : Git-LFS, mais DVC est meilleur pour l'ML.

---

## 1.5 QUALITÉ DE CODE (LINTING & FORMATAGE)

Installe et configure :

- **`ruff`** : linter ultra-rapide (remplace flake8, isort, pyupgrade)
- **`black`** : formateur (ou `ruff format`)
- **`mypy`** : typage statique (strict mode sur `src/ayiti_ai/`)
- **`bandit`** : détection de vulnérabilités
- **`pre-commit`** : orchestrateur qui lance tout avant chaque commit

Fichier `.pre-commit-config.yaml` avec au minimum :
- `ruff` (check + format)
- `mypy`
- `bandit`
- `check-yaml`
- `check-added-large-files` (limite 10 Mo)
- `detect-private-key`
- `gitleaks`

**Règle** : un commit qui ne passe pas pre-commit n'est **pas** poussé. Point.

---

## 1.6 CI / CD (GitHub Actions)

Trois workflows :

### `.github/workflows/ci.yml`
Sur chaque PR et push :
- Setup Python 3.10, 3.11
- `pip install -e ".[dev]"`
- `ruff check .`
- `mypy src/`
- `pytest --cov=src/ayiti_ai --cov-report=xml`
- Upload coverage sur Codecov
- Bandit security scan

### `.github/workflows/data-validation.yml`
Sur modification de `data/` :
- Lance `scripts/collect_data.py --validate`
- Vérifie la présence de champs requis
- Vérifie qu'aucune PII n'a fuité (regex email/téléphone/CIN haïtien)

### `.github/workflows/release.yml`
Sur tag `v*.*.*` :
- Build du package
- Génération de la ModelCard et DataCard
- Publish éventuel sur HuggingFace Hub (si applicable)

---

## 1.7 ENVIRONNEMENTS D'EXÉCUTION

Tu vas travailler sur **3 environnements distincts**, chacun avec ses contraintes :

| Env | Rôle | Contraintes |
|-----|------|-------------|
| **Dell (CPU local)** | Dev, data collection, tests, code review | Pas d'entraînement lourd |
| **Google Colab (T4/A100)** | SFT, ablations, expériences rapides | Session 12h max, disque limité |
| **Cloud GPU (Runpod/Lambda/Vast.ai)** | Entraînement final, longues runs | Coût $/h, budgétise |

Prépare un notebook Colab (`notebooks/02_train_colab.ipynb`) qui :
1. `git clone` du repo
2. `pip install -e .`
3. Monte Google Drive pour persister les checkpoints
4. `dvc pull` pour récupérer les données
5. Lance `python scripts/run_training.py --config config/training_config.yaml`

---

## 1.8 CONTAINERIZATION (DOCKER)

Crée un `deployment/Dockerfile` multi-stage :

- **Stage 1 (`builder`)** : installe les deps, compile ce qui doit l'être
- **Stage 2 (`runtime`)** : image légère (`python:3.11-slim`) avec juste le nécessaire

Objectifs :
- Image < 2 Go
- User non-root
- `HEALTHCHECK` défini
- Support CPU **et** GPU (via `--gpus all`)

Test : `docker build -t ayiti-ai:latest . && docker run --rm ayiti-ai:latest ayiti-chat --help` doit marcher.

---

## 1.9 CHECKLIST DE VALIDATION (PHASE 1)

Ne passe à la Phase 2 (Données) que si **TOUT** est coché :

- [ ] Repo restructuré selon 1.1
- [ ] `pyproject.toml` fonctionne, package installable en editable
- [ ] `.env.example` créé, secrets externalisés
- [ ] DVC initialisé, remote configuré, `data/` versionné
- [ ] `pre-commit install` fait, hooks passent sur tout le repo
- [ ] CI GitHub Actions verte sur `main`
- [ ] Coverage de tests ≥ 60% (avant refacto)
- [ ] Docker build réussit, container tourne
- [ ] README mis à jour avec instructions setup complètes
- [ ] `CONTRIBUTING.md` rédigé (conventions de commit, branches)
- [ ] Licence choisie et fichier `LICENSE` ajouté (cf. fichier 10)
- [ ] Premier ADR écrit : `docs/adr/0001-choix-qwen25-15b.md`

---

## 1.10 ERREURS FRÉQUENTES À ÉVITER

1. **"Je ferai la CI plus tard"** → Non. Sans CI, tu régresses sans t'en rendre compte.
2. **"Je committe les données, c'est pratique"** → Non. Git devient inutilisable en 3 mois.
3. **"Un seul environnement Python"** → Non. Utilise `venv` ou `conda` par projet.
4. **"Pas besoin de Docker, ça marche chez moi"** → Non. Le jour où tu déploies, tu perds 3 semaines.
5. **"Je typerai plus tard"** → Non. Le typage attrape 30% des bugs avant l'exécution.

---

**➡️ Prochaine étape** : `02_STRATEGIE_DE_DONNEES.md`
