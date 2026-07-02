# 🇭🇹 AYITI-AI — Plan d'Exécution Technique Complet (De A à Z)

> **Objectif principal** : Structurer, industrialiser et amener le projet de fine-tuning **Ayiti-AI** (basé sur **Qwen2.5-1.5B-Instruct**) d'un prototype fonctionnel à un service d'intelligence artificielle souverain haïtien de qualité production.

---

## 🗺️ Chronologie Globale (12 Semaines)

Le plan est divisé en **6 phases majeures** réparties sur 12 semaines. Chaque phase a des dépendances strictes et des livrables verrouillés.

```
PHASE 1 : Fondations Techniques → Semaines 1-2  → Reproductibilité, CI/CD, Structuration
PHASE 2 : Stratégie de Données   → Semaines 2-4  → Acquisition, Nettoyage, Splits & Annotation
PHASE 3 : Fine-Tuning SFT        → Semaines 4-6  → Entraînement itératif, Hyperparamètres, tracking
PHASE 4 : Évaluation & Sécurité  → Semaines 6-8  → Benchmarks linguistiques, Juge LLM, Guardrails
PHASE 5 : Déploiement & Serving  → Semaines 9-10 → API FastAPI, Quantization, CLI/Web/Telegram UI
PHASE 6 : Observabilité & Live   → Semaines 10-12→ Prometheus, Grafana, Logs JSON, Release RC & Go-Live
```

---

## 🎯 Phase 1 : Fondations Techniques & Restructuration (S1 - S2)

### 1. Refactoring du Dépôt (`ayiti-ai/`)
Il convient de passer de scripts isolés à un package Python modulaire et installable.
* **Arborescence cible** :
  * `src/ayiti_ai/` : Coeur du package (modules `data/`, `models/`, `training/`, `evaluation/`, `inference/`, `guardrails/`, `rag/`, `utils/`).
  * `config/` : Centralisation des configurations YAML (`training_config.yaml`, `lora_config.yaml`, `inference_config.yaml`, `guardrails.yaml`).
  * `tests/` : Tests unitaires (`tests/unit/`) et d'intégration (`tests/integration/`).
  * `deployment/` : Conteneurisation (`Dockerfile`, `docker-compose.yml`).
  * Fichiers de configuration racine : `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `.gitignore`, `.env.example`.

### 2. Packaging (`pyproject.toml`)
* Abandon des dépendances libres. Configuration d'un fichier `pyproject.toml` avec des versions de dépendances strictement épinglées (pinnées).
* Définition d'un point d'entrée editable (`pip install -e ".[dev]"`) et d'alias CLI :
  * `ayiti-train` -> `ayiti_ai.training.run:main`
  * `ayiti-chat` -> `ayiti_ai.inference.chat:main`
  * `ayiti-eval` -> `ayiti_ai.evaluation.run:main`

### 3. Gestion des Secrets et Données (DVC & Gitleaks)
* **Secrets** : Externalisation de toutes les clés d'API (`HF_TOKEN`, `WANDB_API_KEY`, `OPENAI_API_KEY`) dans un fichier `.env` non suivi.
* **Données** : Initialisation de DVC (Data Version Control) lié à un espace de stockage externe (S3, B2 ou Google Drive) pour éviter de committer de lourds datasets sous Git.
* **Sécurité locale** : Configuration de `gitleaks` et `pre-commit` pour bloquer les commits contenant des secrets ou des clés d'accès.

### 4. CI/CD (GitHub Actions)
* Mettre en place `.github/workflows/ci.yml` exécutant le linting (`ruff`), le typage statique (`mypy --strict`) et les tests unitaires (`pytest --cov`) à chaque Pull Request.

---

## 🗂️ Phase 2 : Ingestion et Stratégie de Données (S2 - S4)

### 1. Cadrage et Taxonomie des Données
Le modèle doit être entraîné sur un corpus structuré et typé. Chaque échantillon doit respecter une taxonomie précise codée dans le dataset :
* `LANG` (Langue & grammaire créole - 15%)
* `CULT` (Culture & traditions haïtiennes - 15%)
* `HIST` (Histoire d'Haïti - 10%)
* `GEO` (Géographie - 5%)
* `EDU` (Éducation & Savoirs - 10%)
* `SANT` (Santé publique - 8%)
* `AGRI` (Agriculture locale - 7%)
* `ECON` (Vie économique & marchés - 8%)
* `DROI` (Droit citoyen & démarches - 5%)
* `DIAL` (Dialogues quotidiens - 12%)
* `PROV` (Proverbes & expressions - 3%)
* `TECH` (Technologie & numérique - 2%)

### 2. Schéma de Données (Validation Pydantic)
* Utilisation d'un schéma JSONL strict validé par Pydantic (`src/ayiti_ai/data/schema.py`) contenant les champs obligatoires : `id`, `instruction`, `output`, `language`, `category`, `source` (`manual | translated | scraped | synthetic`), `quality_score`, `license`.
* Exclusion systématique des PII (données personnelles) via expressions régulières (emails, téléphones haïtiens `+509`, CIN, NIF).

### 3. Collecte et Annotation
* **Milestone MVP** : 1 000 paires d'instructions de qualité.
* **Milestone V1** : 5 000 paires.
* **Milestone V2** : 15 000 paires.
* Auto-hébergement d'une instance **Argilla** pour annoter et valider linguistiquement les paires générées par des collaborateurs natifs ou traduites à partir de datasets de référence (Alpaca/Dolly).

### 4. Splits de Données
* Séparation stricte : **80% Train / 10% Validation / 10% Test (Golden Set)**.
* Splits stratifiés selon la catégorie, la langue et la difficulté à l'aide de `scikit-learn`.

---

## 🏋️ Phase 3 : Fine-Tuning SFT & Optimisation (S4 - S6)

### 1. Iterative Training Loop (Cycles d'entraînement)
Ne pas se fier à un seul run. L'entraînement est planifié de manière incrémentale :
* **Cycle 0** : Sanity check (100 samples) pour valider l'absence de bugs mémoires (OOM) sur GPU Colab T4.
* **Cycle 1** : Premier modèle fonctionnel (1K paires).
* **Cycle 2** : Modèle de référence V0.2 (5K paires) sur GPU cloud (A100).
* **Cycle 3** : Runs d'ablation pour comparer les hyperparamètres et architectures.
* **Cycle 4 & 5** : Runs finaux (10K - 15K paires) avec les meilleurs hyperparamètres figés.

### 2. Formatage et Algorithme (ChatML & QLoRA)
* Utilisation du format ChatML natif de Qwen2.5 pour encapsuler les rôles `system`, `user` et `assistant`.
* Fine-tuning via **QLoRA** (quantisation NF4 4-bit, double quantisation, compute dtype `bfloat16`).
* Modules cibles LoRA configurés sur les projections d'attention (`q_proj`, `k_proj`, `v_proj`, `o_proj`) et de MLP (`gate_proj`, `up_proj`, `down_proj`).
* Tracking d'expérience obligatoire via **Weights & Biases** ou **MLflow** pour chaque run (suivi de la courbe de loss de validation).

---

## 🧪 Phase 4 : Évaluation Scientifique et Sécurité (S6 - S8)

### 1. Métriques Automatiques de Référence
Calcul automatique des scores à chaque fin de cycle d'entraînement sur le dataset de test :
* **BLEU** & **chrF** (via `sacrebleu` avec tokenization multilingue).
* **ROUGE-L** (via `rouge-score`).
* **BERTScore** (utilisant `xlm-roberta-large` pour évaluer la similarité sémantique globale).
* **Perplexité (PPL)** sur les réponses de validation.
* **Métriques spécifiques créoles** : Taux d'anglicismes/francicismes non désirés (`code_switch_ratio`) et conformité orthographique IPN (`kreyol_orthography_score`).

### 2. Évaluation par LLM Juge & Humains
* **LLM-as-a-Judge** : Script interrogeant GPT-4o ou Claude 3.5 Sonnet pour attribuer une note de 1 à 5 sur la fluidité, la pertinence, la factualité et l'adéquation culturelle haïtienne.
* **Évaluation Humaine** : Comité de relecture (3 à 5 locuteurs natifs) pour valider un échantillon représentatif de 100 réponses du modèle.

### 3. Guardrails et Sécurité
* **Filtres d'Entrée (Input Guardrails)** : Détection de prompt injection (jailbreaks) et blocage de mots interdits (armes, substances, auto-mutilation).
* **Filtres de Sortie (Output Guardrails)** : Détection de fuites de données personnelles, de propos haineux ou de diagnostics médicaux.
* **Red Teaming** : Soumission du modèle à un dataset d'attaque de plus de 300 invites adversariales. Le taux de refus d'instructions dangereuses doit être supérieur à **99%**.

---

## 🚀 Phase 5 : Déploiement, Serving & Interfaces (S9 - S10)

### 1. Exportation et Quantification
* Fusion définitive de l'adaptateur LoRA avec le modèle de base (`merge_and_unload`).
* Génération de formats multiples selon les cibles d'inférence :
  * **FP16** pour le développement et l'évaluation haute fidélité.
  * **AWQ 4-bit** pour l'inférence optimisée sur GPU.
  * **GGUF (Q4_K_M & Q5_K_M)** pour l'inférence CPU locale / edge (serveurs locaux, ordinateurs personnels en Haïti).

### 2. Moteur d'Inférence et API (FastAPI)
* Encapsulation du modèle dans une API **FastAPI** compatible avec les SDK OpenAI (standard `/v1/chat/completions`).
* Intégration de moteurs haute performance comme **vLLM** ou **TGI** pour gérer le dynamic batching et le KV cache afin de réduire le temps de premier token (TTFT < 1.5s).
* Ajout de fonctionnalités réseau comme le streaming (SSE) et le Rate Limiting par clé d'API.

### 3. Interfaces Utilisateur
* Déploiement d'une interface web légère **Gradio** ou **Streamlit** pour tester le modèle en interne.
* Développement d'un chatbot interactif sur **Telegram** pour ouvrir le modèle à un groupe de testeurs externes en Haïti.

---

## 📊 Phase 6 : Observabilité, RAG et Go-Live (S10 - S12)

### 1. Indexation RAG (Retrieval-Augmented Generation)
* Intégration optionnelle d'une base de connaissances locale (documents historiques, manuels d'agriculture locaux) stockée dans une base de données vectorielle **Qdrant**.
* Utilisation d'un modèle d'embedding multilingue (`intfloat/multilingual-e5-large`) pour récupérer du contexte de qualité avant la génération.

### 2. Monitoring & Alerting
* Instrumentation de l'API FastAPI avec des métriques de performance exposées au format **Prometheus**.
* Déploiement de **Grafana** pour surveiller en temps réel la latence (p50, p95, p99), le débit de tokens par seconde, le taux d'erreur HTTP et l'utilisation de la VRAM GPU.
* Configuration de logs structurés au format JSON collectés par **Graf Loki**, en veillant à masquer automatiquement toute donnée personnelle saisie par l'utilisateur.

### 3. Processus de Release & Checklist
* Exécution complète de la checklist finale avant production (tous les tests Pytest au vert, couverture du code globale > 80%, absence de régression sur les benchmarks).
* Tenue du meeting formel de **GO/NO-GO** et publication de la fiche technique du modèle (Modelcard) détaillant ses limites et ses biais factuels.
* Déploiement progressif en production (canary deployment de 5% à 100%) derrière HTTPS et CDN (Cloudflare).
