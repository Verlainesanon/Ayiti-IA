# 🇭🇹 AYITI-AI — PLAN MAÎTRE DE A À Z (VERSION ROBUSTE)

> **Objectif** : Transformer le prototype Ayiti-AI en un système d'IA souverain haïtien de qualité production, sécurisé, évaluable, déployable et maintenable.
>
> **Base technique** : Qwen2.5-1.5B-Instruct + LoRA/PEFT + SFT + RAG + Guardrails
>
> **Public cible du plan** : Toi (dev principal) + tout dev senior qui rejoindra le projet.

---

## 🎯 PHILOSOPHIE DU PLAN

Ce plan n'est **pas** un tutoriel. C'est une feuille de route d'ingénierie. Chaque étape a :
- Un **objectif mesurable** (Definition of Done)
- Une **dépendance claire** (ce qui doit être fait avant)
- Un **livrable concret** (fichier, script, métrique, doc)
- Un **critère d'échec** (comment savoir que ça ne marche pas)

Tu ne suis pas les étapes "parce que je te le dis". Tu les suis parce que **chacune bloque la suivante**.

---

## 📚 STRUCTURE DE LA DOCUMENTATION

Ce plan est découpé en **12 fichiers Markdown** thématiques :

| # | Fichier | Sujet | Priorité |
|---|---------|-------|----------|
| 00 | `00_README_MASTER_PLAN.md` | Ce fichier — vue d'ensemble | ⭐⭐⭐ |
| 01 | `01_ENVIRONNEMENT_ET_SETUP.md` | Validation environnement, outillage, CI | ⭐⭐⭐ |
| 02 | `02_STRATEGIE_DE_DONNEES.md` | Collecte, annotation, qualité, licences | ⭐⭐⭐ |
| 03 | `03_ARCHITECTURE_TECHNIQUE.md` | Modules, patterns, refactoring | ⭐⭐⭐ |
| 04 | `04_ENTRAINEMENT_SFT.md` | Pipeline SFT robuste + hyperparamètres | ⭐⭐⭐ |
| 05 | `05_EVALUATION_ET_BENCHMARKS.md` | Métriques, jeux de test, human eval | ⭐⭐⭐ |
| 06 | `06_SECURITE_ET_GUARDRAILS.md` | Filtres, prompt injection, red team | ⭐⭐⭐ |
| 07 | `07_RAG_ET_KNOWLEDGE_BASE.md` | Retrieval Augmented Generation haïtien | ⭐⭐ |
| 08 | `08_DEPLOIEMENT_ET_INFERENCE.md` | API, quantization, serving | ⭐⭐ |
| 09 | `09_MONITORING_ET_OBSERVABILITE.md` | Logs, métriques prod, alerting | ⭐⭐ |
| 10 | `10_GOUVERNANCE_ET_LICENCES.md` | Éthique, souveraineté données, RGPD | ⭐⭐⭐ |
| 11 | `11_ROADMAP_12_SEMAINES.md` | Planning semaine par semaine | ⭐⭐⭐ |
| 12 | `12_CHECKLIST_GO_LIVE.md` | Checklist finale avant production | ⭐⭐⭐ |

---

## 🗺️ VUE D'ENSEMBLE DES 6 PHASES

```
PHASE 1 : FONDATIONS         → Semaines 1-2  → Env, CI/CD, tests, gouvernance
PHASE 2 : DONNÉES            → Semaines 2-4  → Collecte 5K paires, annotation, splits
PHASE 3 : MODÉLISATION       → Semaines 4-6  → SFT robuste, ablations, checkpoints
PHASE 4 : ÉVALUATION         → Semaines 6-7  → Benchmarks + human eval + red team
PHASE 5 : SÉCURITÉ & RAG     → Semaines 7-9  → Guardrails, RAG, filtres
PHASE 6 : PROD & MONITORING  → Semaines 9-12 → API, quantization, observabilité
```

---

## ⚠️ CE QUI MANQUE DANS LE HANDOVER ACTUEL (À CORRIGER EN PRIORITÉ)

En lisant ton document de handover, voici les **10 lacunes critiques** que ce plan comble :

1. **Aucune stratégie de données** : 100 paires seed ≠ un modèle utilisable. Il faut viser 5K-20K.
2. **Pas de séparation train/val/test** : impossible de mesurer l'overfitting.
3. **Pas de guardrails** : le modèle peut divulguer n'importe quoi, halluciner, être toxique.
4. **Pas de versioning des datasets** : DVC / Git-LFS absent.
5. **Pas de tracking d'expériences** : Weights & Biases ou MLflow manquent.
6. **Pas de CI/CD** : les tests tournent en local, pas sur push.
7. **Pas de gouvernance** : qui possède les données ? quelle licence pour le modèle ?
8. **Pas d'évaluation humaine** : BLEU/ROUGE seuls sont insuffisants pour le créole.
9. **Pas de plan de déploiement** : comment servir le modèle ? à qui ? avec quelle latence ?
10. **Pas de monitoring** : une fois en prod, comment détecter la dérive ?

Chacun de ces points a son propre fichier dans ce plan.

---

## 🎓 PRÉREQUIS AVANT DE COMMENCER

Tu dois maîtriser (ou apprendre en cours de route) :
- **Git avancé** : branches, rebase, tags, hooks
- **Python packaging** : `pyproject.toml`, `setuptools`, entry points
- **HuggingFace stack** : `transformers`, `peft`, `trl`, `datasets`, `accelerate`
- **Docker basique** : build, run, compose
- **PyTorch** : autograd, `.to(device)`, mixed precision
- **Statistiques** : intervalle de confiance, test t, corrélation
- **NLP** : tokenization BPE, perplexité, teacher forcing

Si un point te manque, **ne saute pas** — apprends-le avant. Un modèle mal entraîné coûte plus cher en temps que 2 jours d'apprentissage.

---

## 🚨 RÈGLES D'OR (NON NÉGOCIABLES)

1. **Aucune donnée sensible dans Git** : `.gitignore` strict + secrets via `.env` + `git-secrets`.
2. **Aucun commit direct sur `main`** : toujours via Pull Request avec review (même solo, tu review ton propre code après 24h).
3. **Aucun modèle publié sans évaluation complète** : cf. `12_CHECKLIST_GO_LIVE.md`.
4. **Aucune donnée sans licence claire** : cf. `10_GOUVERNANCE_ET_LICENCES.md`.
5. **Toute décision technique est documentée** : dans `docs/adr/` (Architecture Decision Records).
6. **Aucun `print()` en production** : utilise `logging` avec niveaux.
7. **Aucune valeur hardcodée** : tout va dans YAML / .env.
8. **Tout code a un test** : couverture minimale 70%.

---

## 📊 KPI DU PROJET (SUIVIS CHAQUE SEMAINE)

| KPI | Cible S4 | Cible S8 | Cible S12 |
|-----|----------|----------|-----------|
| Paires de données validées | 1 000 | 5 000 | 15 000 |
| Coverage de tests | 60% | 75% | 85% |
| BLEU sur test set ht→fr | > 15 | > 25 | > 35 |
| ROUGE-L | > 0.20 | > 0.35 | > 0.45 |
| Taux de refus guardrail | N/A | > 95% | > 99% |
| Latence inférence (p95, GPU) | N/A | < 3s | < 1.5s |
| Uptime API | N/A | N/A | > 99% |

---

## 🧭 PAR OÙ COMMENCER ?

**Cette semaine (S1)** :
1. Lis intégralement les fichiers 01, 02, 03, 10.
2. Exécute la checklist du fichier 01 (environnement + CI).
3. Choisis ta licence (fichier 10) — c'est bloquant pour tout le reste.
4. Crée les 5 issues GitHub prioritaires (voir `11_ROADMAP_12_SEMAINES.md`).

**Ne touche PAS à l'entraînement tant que la Phase 1 n'est pas verte.**

---

## 📞 ESCALADE ET DÉCISIONS

Certaines décisions te dépassent (juridique, souveraineté). Identifie **dès maintenant** :
- Un **conseiller juridique** (licences, protection données personnelles haïtiennes)
- Un **linguiste créoliste** (validation qualité des données)
- Un **expert cloud** (si tu ne veux pas gérer l'infra toi-même)

Écris leurs noms et contacts dans `docs/stakeholders.md`.

---

**➡️ Prochaine étape** : Ouvre `01_ENVIRONNEMENT_ET_SETUP.md`.
