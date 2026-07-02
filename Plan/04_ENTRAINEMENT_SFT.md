# 04 — ENTRAÎNEMENT SFT (PIPELINE ROBUSTE ET REPRODUCTIBLE)

> **Objectif** : Un pipeline d'entraînement qui produit un modèle mesurable, reproductible, comparable, et déployable — pas juste "un modèle qui a tourné".

---

## 4.1 STRATÉGIE D'ENTRAÎNEMENT GLOBALE

Tu vas faire **plusieurs cycles** d'entraînement, pas un seul :

| Cycle | Objectif | Données | Durée | Environnement |
|-------|----------|---------|-------|---------------|
| **Cycle 0** | Sanity check pipeline | 100 paires | 15 min | Colab T4 |
| **Cycle 1** | MVP fonctionnel | 1 000 paires | 2h | Colab T4 |
| **Cycle 2** | Version alpha | 5 000 paires | 6h | Colab A100 ou Runpod |
| **Cycle 3** | Ablations hyperparamètres | 5 000 paires | 6h × 4-8 runs | Cloud GPU |
| **Cycle 4** | Version bêta | 10 000 paires | 12h | Cloud GPU |
| **Cycle 5** | Version 1.0 finale | 15 000 paires | 18h | Cloud GPU |

**Jamais** un seul entraînement. Toujours plusieurs, comparés.

---

## 4.2 CHOIX FONDAMENTAUX

### 4.2.1 Modèle de base

Confirmé : **Qwen2.5-1.5B-Instruct**.

Justifications à documenter dans `docs/adr/0001-choix-qwen25-15b.md` :
- Multilingue (support fr/en natif, ht apprenable)
- 1.5B = tourne sur T4 gratuit + inférence CPU envisageable
- Licence Apache 2.0 (compatible usage commercial et souverain)
- Bonne performance sur benchmarks small-model

**Alternatives à envisager si Qwen déçoit** :
- `google/gemma-2-2b-it`
- `microsoft/Phi-3.5-mini-instruct`
- `meta-llama/Llama-3.2-3B-Instruct` (attention licence Meta)

Fais un **A/B test** cycle 3 : Qwen vs Gemma vs Phi sur mêmes données. Documente le résultat.

### 4.2.2 Méthode : PEFT (LoRA / QLoRA)

**LoRA** avec quantization NF4 (QLoRA) — c'est le bon choix pour :
- Économie mémoire (T4 16GB suffit)
- Rapidité
- Adaptateurs légers (< 100 MB, versionnables)

Configuration LoRA raisonnable pour Qwen2.5-1.5B :

```yaml
lora:
  r: 16                    # rank — 8 pour économie, 32 pour capacité
  alpha: 32                # généralement 2×r
  dropout: 0.05
  target_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
    - gate_proj             # attention: dépend de l'architecture
    - up_proj
    - down_proj
  bias: "none"
  task_type: "CAUSAL_LM"
```

**À tester en ablation** :
- `r = 8, 16, 32, 64`
- Cibler seulement attention vs attention + MLP
- Différentes valeurs d'alpha

### 4.2.3 Format des données pour le training

Utilise le format **ChatML** natif de Qwen. Chaque exemple est formaté :

```
<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{instruction}
{input}<|im_end|>
<|im_start|>assistant
{output}<|im_end|>
```

Le `system_prompt` inclut l'identité Ayiti-AI (cf. `06_SECURITE_ET_GUARDRAILS.md`).

**Loss masking** : n'entraîne que sur les tokens de la réponse `assistant`, pas sur le prompt (utilise `DataCollatorForCompletionOnlyLM` ou équivalent TRL).

---

## 4.3 HYPERPARAMÈTRES DE DÉPART (POINT DE PARTAGE)

Ces valeurs sont des **points de départ**, pas des vérités. Tu vas les ajuster.

```yaml
training:
  num_train_epochs: 3
  per_device_train_batch_size: 4
  gradient_accumulation_steps: 8       # batch effectif = 32
  learning_rate: 2.0e-4
  lr_scheduler_type: "cosine"
  warmup_ratio: 0.05
  weight_decay: 0.01
  max_grad_norm: 1.0
  optim: "adamw_torch"                  # ou "paged_adamw_8bit" si mémoire
  gradient_checkpointing: true
  bf16: true                            # si A100/H100, sinon fp16
  seed: 42
  logging_steps: 10
  eval_steps: 100
  save_steps: 100
  save_total_limit: 3
  load_best_model_at_end: true
  metric_for_best_model: "eval_loss"
  greater_is_better: false
```

### 4.3.1 Règle du batch effectif

**Batch effectif** = `per_device_batch_size × gradient_accumulation_steps × num_gpus`.

Cible : **32 ou 64**. En dessous → gradients bruités. Au-dessus → mémoire explose ou convergence lente.

### 4.3.2 Learning rate

- Trop haut (> 5e-4) → divergence, `NaN` loss
- Trop bas (< 5e-5) → n'apprend pas
- Sweet spot LoRA : `1e-4` à `3e-4`
- **Warmup** obligatoire (5% des steps) pour éviter chocs initiaux

### 4.3.3 Nombre d'epochs

- Petit dataset (< 2K) : 3-5 epochs
- Moyen (2K-10K) : 2-3 epochs
- Grand (> 10K) : 1-2 epochs
- **Signal d'overfitting** : `eval_loss` remonte alors que `train_loss` continue de baisser → early stopping.

---

## 4.4 CALLBACKS ET MONITORING (NON NÉGOCIABLE)

Chaque entraînement DOIT logger vers :

### 4.4.1 Weights & Biases

- Métriques : loss, eval_loss, learning_rate, grad_norm, tokens/sec
- Config : tout le YAML
- Artefacts : checkpoints intermédiaires (pas juste le final)
- Système : GPU util, memory, temperature
- **Alertes** : email si loss = NaN ou divergence

### 4.4.2 Callbacks custom à implémenter

1. **`SampleGenerationCallback`** : toutes les N steps, génère 5 réponses sur des prompts fixes → visualise l'évolution qualitative
2. **`GradientNormCallback`** : logge la norme des gradients (détecte explosion/vanishing)
3. **`EarlyStoppingCallback`** : patience = 3 évaluations
4. **`BestCheckpointCallback`** : garde meilleur checkpoint selon `eval_loss` **et** BLEU sur mini val set
5. **`OOMRecoveryCallback`** : réduit batch en cas d'OOM (avec log)

### 4.4.3 Logs indispensables à chaque run

- Commit git exact (`git rev-parse HEAD`)
- Version des dépendances (`pip freeze` → artifact W&B)
- Hash du dataset utilisé (DVC hash)
- Seed
- Total tokens traités
- Durée totale
- Coût estimé (si cloud GPU)

Sans ces infos, ton run est **irreproductible**.

---

## 4.5 GESTION DES CHECKPOINTS

- **Fréquence** : tous les 100-500 steps selon durée totale
- **Rétention** : garder 3 derniers + meilleur selon métrique + final
- **Nommage** : `checkpoint-{step}` (convention HF)
- **Stockage** :
  - Local Colab : `/content/drive/MyDrive/ayiti-ai/checkpoints/`
  - Cloud : bucket S3/GCS versionné
  - **Jamais** dans le repo Git
- **Métadonnées** : à chaque checkpoint, sauvegarde un `metadata.json` avec config, métriques, git hash

### 4.5.1 Reprendre un entraînement interrompu

Colab coupe à 12h. Ton code DOIT supporter :
```python
trainer.train(resume_from_checkpoint=True)
```

Test régulièrement cette capacité.

---

## 4.6 STRATÉGIES ANTI-OOM (T4 16GB)

Si tu manques de mémoire :

1. Réduire `per_device_train_batch_size` (mais augmenter grad_accumulation)
2. Activer `gradient_checkpointing`
3. Utiliser `paged_adamw_8bit` (économise 2GB)
4. Réduire `max_seq_length` (mais pas < 1024)
5. Passer à QLoRA 4-bit si pas déjà fait
6. Réduire `r` de LoRA
7. `torch.cuda.empty_cache()` entre eval et train

Ne monte JAMAIS un dernier recours : "reduce dataset". Le dataset est sacré.

---

## 4.7 TRACKING D'EXPÉRIENCES (RIGUEUR SCIENTIFIQUE)

Chaque run a :
- Un **nom** explicite : `sft-v1.2-qlora-r16-lr2e4-3ep`
- Un **groupe** : `ablation-lr` par exemple
- Des **tags** : `qlora`, `full-dataset`, `v1.2`
- Une **description** : ce que tu testes et pourquoi

### 4.7.1 Table de suivi (`experiments.md` ou W&B Reports)

| Run | Modèle | LR | R | Epochs | Dataset | Eval Loss | BLEU | ROUGE-L | Décision |
|-----|--------|----|----|--------|---------|-----------|------|---------|----------|
| exp-001 | Qwen2.5-1.5B | 2e-4 | 16 | 3 | v1 (1K) | 1.42 | 8.3 | 0.19 | Baseline |
| exp-002 | Qwen2.5-1.5B | 1e-4 | 16 | 3 | v1 (1K) | 1.51 | 7.1 | 0.17 | LR trop bas |
| exp-003 | Qwen2.5-1.5B | 3e-4 | 32 | 3 | v1 (1K) | 1.38 | 9.5 | 0.21 | Meilleur → keep |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Documentation continue** > mémoire humaine.

---

## 4.8 ABLATIONS À MENER (SEMAINE 5-6)

Au minimum, teste :

1. **LoRA rank** : 8 vs 16 vs 32
2. **Target modules** : attention only vs attention+MLP
3. **Learning rate** : 1e-4 vs 2e-4 vs 3e-4
4. **Data mix** : 100% ht vs 70/20/10 vs 60/25/15
5. **Epochs** : 2 vs 3 vs 5
6. **Prompt system** : identité forte vs identité neutre
7. **Packing** : on vs off (impact sur throughput)

Chaque ablation change **une seule variable**. Sinon tu ne peux rien conclure.

---

## 4.9 COÛTS ET BUDGET

Estime avant de lancer :

| Plateforme | GPU | $/heure | Cycle typique | Coût |
|-----------|-----|---------|---------------|------|
| Colab Free | T4 (partagé) | 0 | Cycle 0-1 | 0 |
| Colab Pro | T4/L4/A100 | ~10$/mois | Cycle 1-2 | ~10$ |
| Runpod | A100 40GB | ~1.5$/h | Cycle 3-4 | 20-40$ |
| Vast.ai | A100/H100 | 1-3$/h | Cycle 5 | 30-60$ |
| Lambda Labs | A100 | 1.29$/h | Cycle 5 | ~25$ |

**Budget total réaliste projet complet** : 150-300 USD sur 3 mois si tu es prudent.

Toujours logger le coût réel dans le run.

---

## 4.10 CHECKLIST AVANT DE LANCER UN RUN

- [ ] Config YAML validée
- [ ] Dataset version fixée (DVC hash noté)
- [ ] Splits train/val vérifiés (pas de fuite)
- [ ] Modèle de base téléchargé et hash vérifié
- [ ] Test dry-run sur 10 samples → passe
- [ ] W&B initialisé
- [ ] Checkpoints dir vide ou versionné
- [ ] GPU disponible, mémoire suffisante
- [ ] Notification prête (email/Discord si run échoue)
- [ ] Budget/temps estimé et acceptable
- [ ] Nom de run explicite

---

## 4.11 CHECKLIST APRÈS UN RUN

- [ ] `training_loss` a bien décru
- [ ] `eval_loss` a suivi (pas d'explosion en fin)
- [ ] Pas de NaN dans les métriques
- [ ] Meilleur checkpoint identifié
- [ ] Génération manuelle sur 20 prompts test → sensée
- [ ] Métriques BLEU/ROUGE calculées
- [ ] Comparaison avec baseline documentée
- [ ] Artefacts pushés vers stockage long terme
- [ ] Entry créée dans `experiments.md`
- [ ] Prochaine étape décidée (nouveau run vs consolidation)

---

## 4.12 RED FLAGS PENDANT L'ENTRAÎNEMENT

Arrête immédiatement si :

- **Loss = NaN** après quelques steps → LR trop haut, ou données corrompues
- **Loss reste constante** → LR trop bas, ou dataset trop petit/facile
- **Loss descend puis stagne à 0.01** → overfitting massif ou data leak
- **Eval loss remonte fortement** dès l'epoch 1 → overfitting
- **GPU util < 30%** → bottleneck data loading (augmenter workers, packing)
- **Tokens/sec très bas** → problème I/O ou preprocessing lent

---

**➡️ Prochaine étape** : `05_EVALUATION_ET_BENCHMARKS.md`
