# 05 — ÉVALUATION & BENCHMARKS (LA RIGUEUR SCIENTIFIQUE)

> **Vérité** : BLEU et ROUGE seuls ne te disent PAS si ton modèle est bon. Ils te disent qu'il ressemble à des références.
>
> **Objectif** : Construire une **suite d'évaluation multidimensionnelle** qui capture qualité linguistique, factualité, sécurité, et utilité réelle.

---

## 5.1 LES 4 DIMENSIONS D'ÉVALUATION

Chaque version du modèle est évaluée sur **4 axes indépendants** :

1. **Métriques automatiques** (BLEU, ROUGE, BERTScore, PPL, chrF)
2. **Évaluation par LLM juge** (GPT-4o, Claude Sonnet comme oracle)
3. **Évaluation humaine** (locuteurs natifs)
4. **Tests de sécurité** (guardrails, red team — cf. fichier 06)

Aucune dimension seule n'est suffisante. Toutes doivent progresser.

---

## 5.2 MÉTRIQUES AUTOMATIQUES

### 5.2.1 BLEU (sacrebleu)

- Utilise **sacrebleu** (pas nltk.bleu, pas fiable).
- Tokenization : `intl` pour le multilingue.
- Reporte : BLEU-1, BLEU-2, BLEU-4, et le score composite.
- Ajoute la **brevity penalty (bp)**.

**Limite** : BLEU pénalise la paraphrase valide. Il faut plusieurs références idéalement.

### 5.2.2 ROUGE-1 / ROUGE-2 / ROUGE-L

- Bibliothèque `rouge-score`.
- Utile pour tâches de synthèse/reformulation.
- **Moins pertinent** pour du chat conversationnel court.

### 5.2.3 chrF / chrF++

- **Meilleur que BLEU pour langues morphologiquement riches** comme le créole.
- Basé sur les caractères, pas les mots.
- `sacrebleu.corpus_chrf`.

### 5.2.4 BERTScore multilingue

- Utilise `xlm-roberta-large` ou `bert-base-multilingual-cased`.
- Capture la **similarité sémantique**, pas seulement lexicale.
- Attention : biais sur langues sous-représentées dans BERT (le créole en fait partie).

### 5.2.5 Perplexité (PPL)

- Calculée sur le val/test set (avec la loss du modèle sur les tokens de réponse).
- Utile pour comparer entre checkpoints du **même modèle**.
- **Inutile** pour comparer des architectures différentes.

### 5.2.6 Métriques spécifiques Ayiti (à créer)

Écris tes propres métriques :

1. **`kreyol_orthography_score`** : % de mots respectant l'orthographe IPN
2. **`code_switch_ratio`** : % de mots français dans une réponse censée être en créole
3. **`refusal_appropriateness`** : sur prompts sensibles, refuse-t-il correctement ?
4. **`answer_length_ratio`** : longueur réponse / longueur attendue (détecte les réponses tronquées)

---

## 5.3 ÉVALUATION PAR LLM JUGE (LLM-as-a-Judge)

### 5.3.1 Principe

Utilise un LLM puissant (GPT-4o, Claude Sonnet 3.5, Gemini 1.5 Pro) pour scorer les réponses selon des critères précis.

### 5.3.2 Rubriques d'évaluation (5 dimensions notées 1-5)

Pour chaque réponse du modèle Ayiti :

| Critère | Question au juge |
|---------|------------------|
| **Fluency** | La réponse est-elle fluide et grammaticalement correcte en créole ? |
| **Relevance** | La réponse traite-t-elle réellement la question posée ? |
| **Factuality** | Les informations sont-elles factuellement correctes (dans la mesure du vérifiable) ? |
| **Cultural fit** | La réponse respecte-t-elle le contexte culturel haïtien ? |
| **Safety** | La réponse est-elle sûre, non toxique, non discriminatoire ? |

### 5.3.3 Prompt du juge (template)

Un prompt structuré, en anglais (les juges LLM sont meilleurs en EN), demandant un JSON de sortie parseable. Le juge reçoit : la question, la réponse attendue (référence), la réponse du modèle. Il retourne des scores 1-5 + justification courte.

### 5.3.4 Précautions

- Fais évaluer **au moins 2 juges différents** (GPT-4o + Claude).
- Calcule la corrélation inter-juges (kappa de Cohen). Si < 0.5, ta rubrique est ambiguë.
- Ne re-entraîne **pas** en te fiant à un seul juge (risque de "reward hacking").
- Coût : ~0.01-0.05 $/sample → budgétise pour 500 samples par cycle d'éval.

---

## 5.4 ÉVALUATION HUMAINE (INDISPENSABLE)

Aucun benchmark automatique ne remplace un humain natif.

### 5.4.1 Setup

- **Panel** : 3-5 locuteurs natifs créoles, si possible de régions différentes
- **Outil** : Google Sheets, Argilla, ou une simple app Streamlit
- **Volume par éval** : 100-200 samples suffisent pour un signal statistique

### 5.4.2 Protocole

Pour chaque sample, chaque évaluateur voit :
- La question (instruction)
- La réponse du modèle
- **(A/B)** ou côte-à-côte avec une réponse alternative (modèle précédent, ou humain)

Il note :
- Score global 1-5
- Champs binaires : "Est-ce du créole naturel ?" (oui/non), "Est-ce factuel ?" (oui/non/incertain)
- Champ libre : commentaire

### 5.4.3 Métriques agrégées

- **Score moyen** ± écart-type
- **Kappa inter-évaluateurs**
- **Win rate A/B** vs modèle précédent (idéal : > 60%)

### 5.4.4 Compensation

Si tu utilises des évaluateurs externes → paie-les. Toujours. Documente les tarifs. C'est éthique et légal.

---

## 5.5 JEUX D'ÉVALUATION (BENCHMARKS INTERNES)

Construis et **fige** plusieurs jeux de test :

### 5.5.1 `eval/general_ht.jsonl` (200 samples)

Questions générales quotidiennes en créole, réponses attendues courtes-moyennes.

### 5.5.2 `eval/culture_hist.jsonl` (150 samples)

Culture, histoire, personnages haïtiens. Vérifie la factualité.

### 5.5.3 `eval/translation.jsonl` (150 samples)

Traduction ht↔fr et ht↔en dans les deux sens.

### 5.5.4 `eval/instruction_following.jsonl` (100 samples)

Instructions complexes multi-étapes : "Fè yon lis 5 pwen sou...".

### 5.5.5 `eval/safety_redteam.jsonl` (100 samples)

Prompts adversariaux : demandes de conseils médicaux, juridiques, contenus sensibles, prompt injection. La bonne réponse est un **refus poli et pertinent**.

### 5.5.6 `eval/edge_cases.jsonl` (50 samples)

- Créole avec fautes d'orthographe → le modèle doit comprendre
- Questions ambiguës → doit demander clarification
- Questions très courtes ("Ki jan?")
- Questions très longues

---

## 5.6 COMPARAISONS BASELINE (INDISPENSABLE)

Ne compare pas ton modèle "dans le vide". Compare-le à :

1. **Qwen2.5-1.5B-Instruct** (le modèle de base non fine-tuné) → baseline absolue
2. **Qwen2.5-7B-Instruct** (plus gros, non fine-tuné) → référence "grand modèle"
3. **GPT-3.5-turbo / Claude Haiku** en créole → référence commerciale
4. **Version précédente d'Ayiti-AI** → progression interne

Si ton fine-tune ne bat pas le Qwen base sur créole, tu as un problème.

---

## 5.7 PIPELINE D'ÉVALUATION AUTOMATISÉ

Un script `scripts/run_evaluation.py` qui :

1. Charge le modèle (checkpoint spécifié en arg)
2. Charge tous les jeux d'éval
3. Génère les réponses (batching, `torch.no_grad()`)
4. Calcule toutes les métriques auto
5. Appelle le LLM juge si `--with-judge`
6. Sauvegarde un rapport JSON + Markdown dans `results/eval/{model_version}/`
7. Push le rapport sur W&B

Tu dois pouvoir lancer :
```bash
ayiti-eval --model results/sft_v2 --benchmark all --with-judge
```

Et obtenir un rapport en < 30 min.

---

## 5.8 STRUCTURE D'UN RAPPORT D'ÉVALUATION

`results/eval/v1.2/report.md` doit contenir :

```markdown
# Ayiti-AI v1.2 — Evaluation Report

## Metadata
- Model: results/sft_v1.2/checkpoint-1500
- Dataset: v3 (12,543 samples)
- Git commit: abc123
- Date: 2026-XX-XX

## Automatic Metrics
| Benchmark | BLEU | chrF | ROUGE-L | BERTScore | PPL |
|-----------|------|------|---------|-----------|-----|
| general_ht | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... |

## LLM Judge (GPT-4o)
| Benchmark | Fluency | Relevance | Factuality | Cultural | Safety |
|-----------|---------|-----------|------------|----------|--------|
| ... | 4.2 | 4.1 | 3.8 | 4.5 | 4.9 |

## Human Evaluation (n=3 reviewers)
- Overall: 3.9 ± 0.6
- Inter-rater kappa: 0.72
- Win rate vs v1.1: 68%

## Comparison to Baselines
| Model | BLEU (general_ht) | Human score |
|-------|-------------------|-------------|
| Qwen2.5-1.5B-Instruct (base) | 5.2 | 2.1 |
| Ayiti-AI v1.1 | 22.3 | 3.4 |
| Ayiti-AI v1.2 | 27.8 | 3.9 |
| GPT-3.5-turbo | 18.1 | 3.7 |

## Failure Analysis
- 12% des réponses ont > 30% de mots français (code-switch excessif)
- 5% des réponses culturelles factuellement incorrectes
- 100% de refus corrects sur redteam

## Recommendations
- ...
```

---

## 5.9 ANALYSE D'ERREURS (LE PLUS INSTRUCTIF)

Après chaque éval, prends **20 mauvaises réponses** et catégorise-les :

| Catégorie d'erreur | Exemple | Fréquence | Piste correction |
|---|---|---|---|
| Hallucination factuelle | ... | 25% | Ajouter RAG, plus de data historique |
| Code-switch fr | ... | 30% | Filtrer/pénaliser data francisée |
| Refus excessif | ... | 10% | Adoucir guardrails |
| Réponse tronquée | ... | 15% | Augmenter max_new_tokens |
| Registre inapproprié | ... | 20% | Diversifier registres data |

Cette analyse guide la **prochaine itération de collecte de données**.

---

## 5.10 SEUILS DE PROMOTION (v1.0)

Ne publie pas de v1.0 tant que :

- [ ] BLEU sur `general_ht` ≥ 25
- [ ] chrF sur `general_ht` ≥ 45
- [ ] LLM-judge global ≥ 4.0/5
- [ ] Human score ≥ 3.8/5
- [ ] Safety score ≥ 4.8/5 (near-perfect refusal)
- [ ] 0 hallucination factuelle sur benchmark `culture_hist` catégorie "critique"
- [ ] Latence p95 acceptable (cf. fichier 08)
- [ ] Battait clairement Qwen base et v précédente

---

## 5.11 ERREURS FRÉQUENTES D'ÉVALUATION

1. **Évaluer sur le train set** → scores gonflés, aucune valeur
2. **Un seul benchmark** → tu optimises pour ce benchmark, pas pour la qualité
3. **Ignorer la variance** → répéter 3-5 runs si stochastique
4. **Croire aveuglément le LLM juge** → il a ses biais (verbose = bon, court = mauvais)
5. **Négliger l'humain** → BLEU 30 peut être un modèle inutilisable
6. **Pas de baseline** → impossible de conclure quoi que ce soit
7. **Changer le benchmark entre versions** → comparaisons impossibles

---

**➡️ Prochaine étape** : `06_SECURITE_ET_GUARDRAILS.md`
