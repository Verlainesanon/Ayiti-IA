# 🇭🇹 Ayiti-AI — Progression de l'implémentation du système LID

Ce fichier suit l'état d'avancement de l'implémentation du système de Détection de Langue (Language IDentification - LID) triple couche pour Ayiti-AI.

## 📊 État global
- **Phase actuelle** : Phase 2 — Niveaux 1 & 2 implémentés (Semaine 2)
- **Progression globale** : 55% (Semaine 1 complète ✅, Semaine 2 en cours 80%)

---

## 🗺️ Checklist d'exécution

### 1. Fondations & Conception (Semaine 1)
- `[x]` **Task 1.1** — Lecture intégrale des fichiers de spécification (`00`, `01`, `02`) ✅
- `[x]` **Task 1.2** — Choix de la stratégie de code-switching (Option B : Multi-labels avec score) ✅
- `[x]` **Task 1.3** — Rédaction de l'ADR d'architecture (`docs/adr/lid_0001_architecture_pyramide.md`) ✅
- `[x]` **Task 1.4** — Création de la configuration des marqueurs validés (`config/lid_markers.yaml`) v1.0 ✅
- `[x]` **Task 1.5** — Création du squelette technique et des interfaces (`LIDLevel`, Pydantic schemas) ✅
- `[x]` **Task 1.6** — Configuration globale du module (`config/lid_config.yaml`) ✅

### 2. Niveaux 1 & 2 + Données (Semaine 2)
- `[x]` **Task 2.1** — Implémentation du pré-traitement (normalisation NFC, tokenisation robuste) ✅
- `[x]` **Task 2.2** — Implémentation du Niveau 1 (Règles déterministes et diacritiques) ✅
- `[x]` **Task 2.3** — Intégration du Niveau 2 (FastText `lid.176.ftz`) + téléchargement modèle ✅
  - ⚠️ Note : `lid.176.bin` (131 Mo) impossible à DL (disque plein). Utilisation de `lid.176.ftz` (917 Ko) avec seuils adaptés.
  - `fasttext-langdetect` installé (wheels Python 3.13 Windows — aucune compilation C++ requise).
- `[x]` **Task 2.4** — Implémentation de l'orchestrateur `RobustLID` et du Cache LRU ✅
  - Pipeline `pipeline.py` : cascade Niveau 1→2, fail-safe, cache LRU en mémoire, validation Pydantic.
  - **6/6 tests passent** (preprocessing, Level1, Level2, intégration pipeline end-to-end).
- `[ ]` **Task 2.5** — Collecte de données LID initiales (30k+ phrases)

### 3. Niveau 3 + Évaluation (Semaine 3)
- `[ ]` **Task 3.1** — Constitution du Golden Set et splits stratifiés
- `[ ]` **Task 3.2** — Implémentation et entraînement du Niveau 3 (CharCNN)
- `[ ]` **Task 3.3** — Évaluation scientifique et rapport de benchmark (F1 >= 0.92)

### 4. Déploiement & Monitoring (Semaine 4)
- `[ ]` **Task 4.1** — Intégration du LID dans l'application Ayiti-AI (guardrails d'inférence)
- `[ ]` **Task 4.2** — Métriques Prometheus et Dashboards Grafana
- `[ ]` **Task 4.3** — Dockerisation, tests d'intégration complets et déploiement canary

---

## ⏱️ Journal des actions

| Date | Tâche | Statut | Résultat / Commentaire |
|------|-------|--------|------------------------|
| 2026-07-03 | Lecture du plan | Complété | Fichiers 00, 01, 02 lus et assimilés. |
| 2026-07-03 | Stratégie code-switching | Décidée | Option B (multi-labels avec exposition binaire en façade). |
| 2026-07-03 | ADR d'architecture | Complété | ADR rédigé sous docs/adr/lid_0001_architecture_pyramide.md. |
| 2026-07-03 | Marqueurs YAML | Complété | Fichier config/lid_markers.yaml v1.0 créé et validé. |
| 2026-07-03 | Config générale YAML | Complété | Fichier config/lid_config.yaml créé. |
| 2026-07-03 | Squelette & Interfaces | Complété | Protocol LIDLevel, Pydantic schemas (LIDInput, LIDResult, LevelResult) et exceptions.py créés. |
| 2026-07-03 | Pré-traitement | Complété | Détection de script, normalisation NFC, tokenisation Unicode robuste dans preprocessing.py. |
| 2026-07-03 | Niveau 1 (Règles) | Complété | Algorithme de détection par marqueurs, ngrams et diacritiques implémenté dans level1_rules.py avec 4 tests unitaires validés (100% pass). |
| 2026-07-03 | FastText install | Complété | `fasttext-langdetect` + `fasttext-predict` installés (wheels Python 3.13 Windows). `fasttext-wheel` refusé (pas de MSVC 14). |
| 2026-07-03 | Modèle FTZ | Complété | `lid.176.ftz` (917 Ko) téléchargé avec succès. `lid.176.bin` (131 Mo) impossible (disque plein). Seuils adaptés pour ftz. |
| 2026-07-03 | Niveau 2 (FastText) | Complété | `level2_fasttext.py` implémenté avec seuil min_confidence=0.40 adapté au modèle ftz. FR+EN: >0.98, HT long: >0.39. |
| 2026-07-03 | Pipeline RobustLID | Complété | `pipeline.py` : orchestrateur 3 niveaux, fail-safe, cache LRU, early exits (script non-latin, texte vide). 6/6 tests pass. |
