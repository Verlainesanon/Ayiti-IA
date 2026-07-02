# 11 — ROADMAP 12 SEMAINES (PLANIFICATION OPÉRATIONNELLE)

> **Objectif** : Un plan semaine par semaine, avec livrables clairs, pour passer du prototype actuel à une v1.0 déployable.

---

## VUE D'ENSEMBLE

| Semaine | Focus principal | Livrable clé | Phase |
|---------|-----------------|--------------|-------|
| S1 | Fondations env + gouvernance | Repo restructuré, licences choisies | 1 |
| S2 | Setup outillage + collecte début | CI verte, 500 paires collectées | 1-2 |
| S3 | Collecte massive données | 2000 paires curated | 2 |
| S4 | MVP training (Cycle 1) | Modèle v0.1 sur 2K paires, éval initiale | 2-3 |
| S5 | Refactoring code + guardrails minimal | Package `ayiti_ai` propre, guardrails L2 | 3-4 |
| S6 | Cycle 2 training + ablations | Modèle v0.2 sur 5K, ablations documentées | 4 |
| S7 | Évaluation complète + red team v1 | Rapport d'éval v0.2, red team dataset | 5 |
| S8 | Guardrails complets + tests sécurité | Toutes couches actives, ≥95% PASS | 6 |
| S9 | API + WebUI + Bot Telegram | Bêta interne accessible | 8 |
| S10 | RAG (optionnel) + monitoring | Grafana dashboards, Prometheus | 7, 9 |
| S11 | Cycle 5 final + éval finale | Modèle v1.0-rc, rapport complet | 4-5 |
| S12 | Bêta publique + doc + comms | v1.0 déployée, tout public | 6-10 |

---

## SEMAINE 1 : FONDATIONS

### Objectif de la semaine
Décisions fondatrices + squelette du projet propre.

### Tâches (par priorité)

**Lundi**
- Lire intégralement les 12 fichiers de ce plan
- Rédiger `docs/governance/foundational_decisions.md`
- Choisir licence code / modèle / données

**Mardi**
- Créer nouvelle arborescence complète (fichier 01, section 1.1)
- Migrer le code existant dans `src/ayiti_ai/`
- Écrire `pyproject.toml` propre
- `pip install -e ".[dev]"` fonctionne

**Mercredi**
- Configurer `pre-commit` (ruff, black, mypy, bandit)
- Écrire `.env.example`
- Configurer `.gitignore` complet
- Setup DVC + remote (S3 ou Google Drive)

**Jeudi**
- Configurer GitHub Actions : `ci.yml` (tests + lint)
- Configurer secrets GitHub (HF_TOKEN, WANDB_API_KEY)
- Push initial → CI verte

**Vendredi**
- Rédiger `README.md` propre
- Rédiger `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- Fichier `LICENSE` en place
- Premier ADR : `docs/adr/0001-choix-qwen25-15b.md`

### Definition of Done S1
- [ ] Repo restructuré, package installable
- [ ] CI verte
- [ ] DVC initialisé
- [ ] Licences choisies et documentées
- [ ] `foundational_decisions.md` rédigé

---

## SEMAINE 2 : OUTILLAGE + DÉBUT COLLECTE

### Objectif
Outils de qualité de données en place + première vague de collecte.

### Tâches

**Lundi-Mardi**
- Refactoring `src/ayiti_ai/data/schema.py` avec Pydantic
- Refactoring `dataset_builder.py` : classes propres, tests
- Écriture `scripts/data_quality.py` (dédup, PII, langue)

**Mercredi**
- Déploiement Argilla (self-host, Docker Compose)
- Import des données seed existantes dans Argilla
- Rédaction guide d'annotation `docs/annotation_guide.md`

**Jeudi-Vendredi**
- Collecte + annotation quotidienne (2h/jour minimum)
- Cible : 500 paires nouvelles curated
- Splits train/val/test générés (reproductibles, seed=42)

### Livrables
- Pipeline data qualité fonctionnel
- Argilla accessible
- 500 paires curated dans `data/raw/curated/`
- Splits `train.parquet`, `val.parquet`, `test.parquet`

---

## SEMAINE 3 : COLLECTE MASSIVE

### Objectif
Passer à 2000 paires curated de qualité.

### Tâches

**Toute la semaine**
- 4h/jour de collecte + annotation
- Diversification catégories (viser équilibre taxonomie)
- Recruter 1-2 collaborateurs natifs si possible
- Notebook `notebooks/01_eda.ipynb` : EDA complète

### Focus qualité
- Aucune catégorie < 5%
- Ratio ht/fr/en respecté (70/20/10)
- Pas de doublons flous > 85%
- Aucune PII détectée
- Score qualité moyen ≥ 0.7 après revue

### Livrables
- 2000 paires curated
- Datacard v1 rédigée
- EDA notebook publié

---

## SEMAINE 4 : MVP TRAINING (CYCLE 1)

### Objectif
Premier vrai entraînement + première évaluation.

### Tâches

**Lundi**
- Refactor `src/ayiti_ai/training/` : trainer propre, callbacks
- Setup Weights & Biases (projet créé, secrets configurés)

**Mardi**
- Cycle 0 (sanity check) : 100 samples, 100 steps, sur Colab T4
- Vérifier : loss descend, checkpoint sauvegardé, aucune erreur
- Test resume-from-checkpoint

**Mercredi-Jeudi**
- Cycle 1 : entraînement sur 2000 paires, 3 epochs, Colab T4
- Config `config/training_config_v1.yaml` figée et loggée
- Résultats sur W&B

**Vendredi**
- Écriture `scripts/run_evaluation.py`
- Métriques BLEU/chrF/ROUGE/PPL sur test set
- Comparaison avec Qwen2.5-1.5B base non fine-tuné
- Rapport `results/eval/v0.1/report.md`

### Definition of Done S4
- [ ] Modèle v0.1 entraîné et versionné
- [ ] Rapport d'éval publié
- [ ] BLEU sur `general_ht` > 10 (baseline modeste)
- [ ] Bat le modèle de base sur créole (sinon → analyse)

---

## SEMAINE 5 : REFACTORING + GUARDRAILS L2

### Objectif
Code de qualité production + première couche de guardrails.

### Tâches

**Lundi-Mardi**
- Refactoring complet `src/ayiti_ai/` : Pydantic partout, logging structuré, exceptions custom
- Coverage tests > 75%
- Type hints 100%, `mypy --strict` passe

**Mercredi**
- Implémentation `src/ayiti_ai/guardrails/input_filter.py`
- Blocklist YAML de base
- Détection prompt injection basique

**Jeudi**
- Système prompts multi-langues (ht/fr/en) finalisés
- Refus templates dans dataset (500 paires ajoutées)

**Vendredi**
- Tests intégration guardrails
- Documentation `docs/security_model.md`

---

## SEMAINE 6 : CYCLE 2 + ABLATIONS

### Objectif
Modèle v0.2 amélioré + comprendre les hyperparamètres.

### Tâches

**Lundi**
- Data v2 : ajout des 500 refus + collecte hebdo → ~5000 paires
- Config `training_config_v2.yaml`

**Mardi**
- Cycle 2 : full run sur A100 (Runpod ou Colab Pro+)
- ~6h d'entraînement

**Mercredi-Jeudi**
- Ablations parallèles (4-6 runs) :
  - LR : 1e-4 / 2e-4 / 3e-4
  - Rank LoRA : 8 / 16 / 32
  - Modules cibles : attention only vs +MLP
- Chaque run tracé sur W&B

**Vendredi**
- Analyse comparative
- Choix de la config gagnante
- Documentation ADR : `docs/adr/0002-hyperparameter-choice.md`

---

## SEMAINE 7 : ÉVAL COMPLÈTE + RED TEAM V1

### Objectif
Comprendre finement les capacités et failles du modèle.

### Tâches

**Lundi-Mardi**
- Constitution des benchmarks (fichier 05, section 5.5)
- 5-6 benchmarks fichiers JSONL (~750 samples total)

**Mercredi**
- Éval automatique complète : BLEU, chrF, ROUGE, BERTScore
- LLM-as-a-judge (GPT-4o) sur 200 samples
- Coût : ~10-20 USD

**Jeudi**
- Recrutement panel humain (3-5 natifs)
- Session d'éval humaine : 100 samples

**Vendredi**
- Red team dataset v1 : 100 attaques
- Analyse d'erreurs (fichier 05, section 5.9)
- Rapport `results/eval/v0.2/report.md`

---

## SEMAINE 8 : GUARDRAILS COMPLETS

### Objectif
Toutes les couches de défense actives et testées.

### Tâches

**Lundi**
- `output_filter.py` : détection PII sortante, toxicité
- Détection code-switch excessif

**Mardi**
- Classifieur topic léger (embedding + LR)
- Fine-tuner sur 500 exemples annotés

**Mercredi**
- Extension red team dataset à 300 attaques
- Test complet du pipeline

**Jeudi**
- Kill switch implémenté et testé
- Feature flags via config

**Vendredi**
- Ajout dataset SFT : diversification refus (200 paires)
- Préparation Cycle 3 avec data enrichie

### Definition of Done S8
- [ ] Red team ≥ 95% PASS
- [ ] Kill switch fonctionnel
- [ ] Aucune fuite PII détectée sur benchmark
- [ ] Documentation sécurité publiée

---

## SEMAINE 9 : API + INTERFACES

### Objectif
Le modèle est utilisable par des humains.

### Tâches

**Lundi**
- API FastAPI : endpoints `/v1/chat/completions`, `/health`, `/metrics`
- Auth API Key
- Rate limiting (slowapi)

**Mardi**
- Streaming SSE fonctionnel
- Tests intégration API (pytest + httpx)

**Mercredi**
- WebUI Streamlit ou Gradio
- Historique conversation
- Feedback (thumbs)

**Jeudi**
- Bot Telegram basique
- Commandes de base : /start, /help, /lang, /feedback

**Vendredi**
- Dockerisation complète
- Docker Compose : API + Redis + Postgres
- Documentation `docs/deployment.md`

### Livrables
- API accessible sur bêta interne
- WebUI publique (accès sur invitation)
- Bot Telegram fonctionnel

---

## SEMAINE 10 : RAG + MONITORING

### Objectif
Réduire hallucinations + voir ce qui se passe.

### Tâches

**Lundi-Mardi (RAG — si tu as bandwidth)**
- Corpus initial : Wikipedia HT + constitution (500 docs)
- Chunking + embedding (multilingual-e5)
- Qdrant self-host
- Retrieval endpoint intégré

**Mercredi**
- Prometheus + Grafana Docker Compose
- Instrumentation FastAPI (métriques par endpoint)
- Loki pour logs structurés

**Jeudi**
- 5 dashboards Grafana (fichier 09, section 9.5)
- Alertes Slack (webhook)

**Vendredi**
- OpenTelemetry tracing basique
- Playbooks incident (top 3)

---

## SEMAINE 11 : CYCLE FINAL

### Objectif
Le meilleur modèle possible avant release.

### Tâches

**Lundi**
- Data v3 : 10K-15K paires (collecte a continué en parallèle)
- Ajout exemples RAG (500) et refus (500)
- Split v3 propre

**Mardi-Mercredi**
- Cycle 5 : run final sur A100 (~18h)
- Best config selon ablations S6
- Monitoring en temps réel

**Jeudi**
- Éval complète (auto + LLM judge + humain)
- Red team complet
- Rapport `results/eval/v1.0-rc/report.md`

**Vendredi**
- Décision GO / NO-GO release
- Si GO : export, quantization, versionnage v1.0.0
- Modelcard + datacard finales

---

## SEMAINE 12 : GO-LIVE

### Objectif
Ouverture publique contrôlée.

### Tâches

**Lundi**
- Checklist go-live (fichier 12)
- Deploy prod (canary 5% → 25% → 50% → 100%)
- DNS / HTTPS / Cloudflare

**Mardi**
- Documentation publique (site + docs API)
- Communication : blog post, README à jour

**Mercredi**
- Annonce (LinkedIn, Twitter/X, communautés HT)
- Ouverture bêta publique sur invitation
- Monitoring en temps réel

**Jeudi**
- Réponse aux premiers retours
- Hotfix éventuels
- Post-mortem prêt à écrire

**Vendredi**
- Rétrospective 12 semaines
- Rédaction roadmap v1.1 (3 prochains mois)
- Célébration 🇭🇹🎉

---

## GESTION DE PROJET

### Outil de suivi

- **GitHub Projects** : Kanban intégré (To Do / In Progress / Review / Done)
- Chaque tâche = **1 issue** avec label (`priority`, `phase`, `area`)
- Milestones = fin de phase (S4, S8, S12)

### Rituels

- **Daily** (5 min, à toi-même) : "hier / aujourd'hui / bloqueurs"
- **Weekly review** (vendredi 30 min) : progression vs plan, ajustements
- **Mensuel** : rétrospective + ajustement roadmap

### Buffer et incertitude

Ce plan est **ambitieux**. Prévoir :
- 20% de buffer par semaine pour imprévus
- Si retard de 2 semaines → réduire le scope (RAG optionnel, bêta interne only)
- Si retard > 4 semaines → refonte du plan

---

## PIÈGES CLASSIQUES DU SOLO ML

1. **Passer 3 semaines sur la CI, aucun modèle** → équilibre 60/40 outillage/ML
2. **Coder au lieu de collecter** → data > code, toujours
3. **Ignorer les tests → régression cachée** → CI must be green
4. **Publier trop vite → réputation ruinée** → seuil de promotion strict
5. **Ne pas communiquer → projet invisible → aucun feedback → mort douce** → communique dès S6

---

## PLAN B (SI TU ES RETARD)

Si à S8 tu n'as que 2000 paires et pas de modèle v0.2 satisfaisant :

**Version light** :
- Skip RAG (S10)
- Skip Bot WhatsApp (garde Telegram)
- Bêta interne only en S12 (pas de public)
- Focus sur qualité data > quantité modèle

**Il vaut mieux une V0.5 solide qu'une V1.0 branlante.**

---

**➡️ Prochaine étape** : `12_CHECKLIST_GO_LIVE.md`
