# 03 — ARCHITECTURE TECHNIQUE (REFACTORING VERS UNE BASE ROBUSTE)

> **Objectif** : Passer d'un ensemble de scripts qui marchent à une **architecture logicielle** propre, testable, extensible.

---

## 3.1 PRINCIPES DIRECTEURS

1. **Séparation des responsabilités** (SoC) : chaque module fait UNE chose.
2. **Injection de dépendances** : rien n'est instancié en dur dans les fonctions métier.
3. **Configuration externe** : tout paramètre ajustable est dans YAML/env.
4. **Interfaces stables** : les modules communiquent via des contrats explicites (Pydantic models, `Protocol`, `abc.ABC`).
5. **Testabilité maximale** : chaque fonction pure isolable et mockable.
6. **Fail fast, fail loud** : erreurs détectées le plus tôt possible, jamais silencieuses.

---

## 3.2 ARCHITECTURE EN COUCHES

```
┌───────────────────────────────────────────────────────────────┐
│  COUCHE 6 : INTERFACE UTILISATEUR                             │
│  (CLI, API REST, WebUI, Chatbot Telegram/WhatsApp)            │
├───────────────────────────────────────────────────────────────┤
│  COUCHE 5 : ORCHESTRATION                                     │
│  (Chat manager, session, historique, routage)                 │
├───────────────────────────────────────────────────────────────┤
│  COUCHE 4 : GUARDRAILS & POST-PROCESSING                      │
│  (Filtres, censure, validation, formatting)                   │
├───────────────────────────────────────────────────────────────┤
│  COUCHE 3 : INFÉRENCE MODÈLE                                  │
│  (Génération, decoding, sampling, batching)                   │
├───────────────────────────────────────────────────────────────┤
│  COUCHE 2 : MODÈLE                                            │
│  (Qwen + LoRA loader, tokenizer, quantization)                │
├───────────────────────────────────────────────────────────────┤
│  COUCHE 1 : DONNÉES                                           │
│  (Ingestion, validation, dataset builder, RAG index)          │
└───────────────────────────────────────────────────────────────┘
```

Chaque couche ne connaît **que la couche directement inférieure** (dépendance descendante).

---

## 3.3 MODULES CIBLES (`src/ayiti_ai/`)

### 3.3.1 `data/`

- `schema.py` : modèles Pydantic (`InstructionSample`, `DatasetMetadata`)
- `loader.py` : lecture JSONL/Parquet/CSV avec validation
- `builder.py` : `AyitiDatasetBuilder` refactoré
- `cleaner.py` : `TextCleaner` (fonctions pures)
- `splitter.py` : splits stratifiés reproductibles
- `deduplicator.py` : hash + fuzzy dedup
- `quality.py` : détection PII, toxicité, doublons
- `augmentation.py` : back-translation, paraphrase

### 3.3.2 `models/`

- `base.py` : classe abstraite `AyitiModel` (Protocol)
- `qwen_loader.py` : refactoré (retourne un dataclass, pas un tuple)
- `lora_adapter.py` : builder pattern
- `quantization.py` : NF4, GPTQ, AWQ (support multiple backends)
- `merger.py` : fusion LoRA + base model (pour export)
- `registry.py` : registre des modèles disponibles

### 3.3.3 `training/`

- `trainer.py` : refactoré, sans état global
- `callbacks.py` : W&B, MLflow, early stopping custom, checkpoint sur métriques
- `optimizer.py` : builder pour AdamW, Lion, etc.
- `scheduler.py` : cosine, linear, custom warmup
- `data_collator.py` : ChatML formatter propre
- `curriculum.py` : (optionnel) curriculum learning

### 3.3.4 `evaluation/`

- `metrics.py` : BLEU, ROUGE, PPL, chrF, BERTScore
- `benchmarks.py` : jeux d'évaluation standardisés
- `llm_judge.py` : évaluation par LLM externe (GPT-4o)
- `human_eval.py` : outil de scoring humain
- `analysis.py` : matrices de confusion, worst cases, drift

### 3.3.5 `inference/`

- `engine.py` : `InferenceEngine` (interface unique)
- `sampling.py` : stratégies (greedy, top-k, top-p, temperature)
- `streaming.py` : streaming token-by-token
- `batching.py` : dynamic batching pour serving
- `cache.py` : KV cache management

### 3.3.6 `guardrails/`

- `input_filter.py` : pré-filtrage prompt (mots interdits, prompt injection)
- `output_filter.py` : post-filtrage réponse (toxicité, PII, faits sensibles)
- `topic_classifier.py` : classifieur "hors-scope" (léger, embedding-based)
- `refusal.py` : messages de refus multilingues
- `red_team.py` : suite de tests adversariaux

### 3.3.7 `rag/`

- `indexer.py` : construction d'index vectoriel (FAISS/Qdrant)
- `retriever.py` : recherche sémantique multilingue
- `chunker.py` : découpage intelligent (respecte les phrases créoles)
- `embedder.py` : `intfloat/multilingual-e5-large` ou équivalent
- `pipeline.py` : orchestration RAG complète

### 3.3.8 `utils/`

- `logging.py` : logger structuré (JSON logs)
- `config.py` : chargeur YAML + validation Pydantic
- `hf_utils.py` : téléchargement, cache, retry
- `io.py` : safe read/write, atomic operations
- `timing.py` : décorateurs de mesure de performance

---

## 3.4 CONTRATS D'INTERFACE (exemples de patterns)

### 3.4.1 Modèle Pydantic pour un sample

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional

class InstructionSample(BaseModel):
    id: str
    instruction: str = Field(min_length=5, max_length=500)
    input: Optional[str] = None
    output: str = Field(min_length=5, max_length=2000)
    language: Literal["ht", "fr", "en"]
    category: Literal["LANG","CULT","HIST","GEO","EDU","SANT","AGRI","ECON","DROI","DIAL","PROV","TECH"]
    source: str
    quality_score: float = Field(ge=0, le=1, default=0.0)
    # ...
```

### 3.4.2 Config typée

```python
class TrainingConfig(BaseModel):
    model_name: str
    dataset_path: Path
    output_dir: Path
    num_epochs: int
    learning_rate: float
    lora: LoraConfig
    optimizer: OptimizerConfig
    logging: LoggingConfig
```

Chargée par : `TrainingConfig(**yaml.safe_load(open(path)))`.
Validation automatique — si un YAML est cassé, l'erreur est **explicite**.

### 3.4.3 Interface `InferenceEngine`

```python
from typing import Protocol, Iterator

class InferenceEngine(Protocol):
    def generate(self, prompt: str, **kwargs) -> str: ...
    def generate_stream(self, prompt: str, **kwargs) -> Iterator[str]: ...
    def generate_batch(self, prompts: list[str], **kwargs) -> list[str]: ...
```

Ainsi tu peux swap : HF Transformers, vLLM, TGI, llama.cpp — sans changer le reste.

---

## 3.5 CONFIGURATION (YAML STRUCTURÉ)

### 3.5.1 `config/training_config.yaml` (exemple structure)

```yaml
run:
  name: "sft-v1.0-ht"
  seed: 42
  output_dir: "results/sft_v1"

model:
  name_or_path: "Qwen/Qwen2.5-1.5B-Instruct"
  quantization:
    enabled: true
    type: "nf4"
    compute_dtype: "bfloat16"

lora:
  r: 16
  alpha: 32
  dropout: 0.05
  target_modules: ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
  bias: "none"

data:
  train_path: "data/processed/train.parquet"
  val_path: "data/processed/val.parquet"
  max_seq_length: 2048
  packing: true

training:
  num_train_epochs: 3
  per_device_train_batch_size: 4
  gradient_accumulation_steps: 8
  learning_rate: 2.0e-4
  lr_scheduler_type: "cosine"
  warmup_ratio: 0.05
  weight_decay: 0.01
  optim: "adamw_torch"
  gradient_checkpointing: true
  bf16: true
  logging_steps: 10
  eval_steps: 200
  save_steps: 200
  save_total_limit: 3
  load_best_model_at_end: true
  metric_for_best_model: "eval_loss"

logging:
  wandb:
    enabled: true
    project: "ayiti-ai"
    entity: "your-team"
  mlflow:
    enabled: false
```

Aucune valeur numérique dans le code. Tout ici.

---

## 3.6 LOGGING STRUCTURÉ

Remplace **tous** les `print()` par `logging` :

```python
import structlog
logger = structlog.get_logger()

logger.info("training.started",
            run_id=run_id, num_samples=len(dataset), model=model_name)
```

Sortie JSON parsable → indispensable pour analyse a posteriori.

Configure les niveaux :
- `DEBUG` : détails internes
- `INFO` : événements normaux
- `WARNING` : anomalies non bloquantes
- `ERROR` : échecs récupérables
- `CRITICAL` : arrêt

---

## 3.7 GESTION D'ERREURS

### 3.7.1 Hiérarchie d'exceptions custom

```python
class AyitiError(Exception): pass

class DataError(AyitiError): pass
class DataValidationError(DataError): pass
class DataNotFoundError(DataError): pass

class ModelError(AyitiError): pass
class ModelLoadError(ModelError): pass

class InferenceError(AyitiError): pass
class GuardrailBlockedError(AyitiError): pass
```

Ainsi le code appelant catch de façon précise.

### 3.7.2 Règles

- Jamais `except Exception: pass`
- Toujours logger avant de re-raise
- Ne jamais avaler une exception silencieusement
- Utiliser `tenacity` pour retry sur opérations réseau

---

## 3.8 TESTS (STRATÉGIE)

### 3.8.1 Pyramide de tests

```
        /\
       /  \    E2E (5%)
      /----\
     /      \  Integration (25%)
    /--------\
   /          \  Unit (70%)
  /____________\
```

### 3.8.2 Répartition

- **Unit** (`tests/unit/`) : fonctions pures, mocking systématique
- **Integration** (`tests/integration/`) : plusieurs modules ensemble, fixtures partagées
- **E2E** (`tests/e2e/`) : pipeline complet mini (100 paires → mini-train → eval)

### 3.8.3 Fixtures indispensables

- `tests/fixtures/mini_dataset.jsonl` : 20 paires de test
- `tests/fixtures/mock_config.yaml`
- `tests/conftest.py` : fixtures pytest partagées

### 3.8.4 Couverture cible

- Global : **≥ 80%**
- Modules critiques (data, guardrails) : **≥ 95%**
- Configuration dans `pyproject.toml`

---

## 3.9 REPRODUCTIBILITÉ (SEEDS PARTOUT)

Une seule fonction, appelée au démarrage :

```python
def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ["PYTHONHASHSEED"] = str(seed)
    transformers.set_seed(seed)
```

Le `seed` vient toujours du config YAML, jamais hardcodé.

---

## 3.10 MIGRATION PROGRESSIVE (SI TU HÉSITES)

Ne refactor **pas** tout d'un coup. Ordre suggéré :

1. Semaine 1 : Setup env, packaging, tests, CI
2. Semaine 2 : Refactor `data/` (schéma Pydantic, splits)
3. Semaine 3 : Refactor `models/` + `training/`
4. Semaine 4 : Ajout guardrails minimal
5. Semaine 5+ : Le reste

Chaque refactor a sa PR, sa suite de tests verte, sa description claire.

---

## 3.11 CHECKLIST PHASE 3

- [ ] Structure `src/ayiti_ai/` en place avec sous-modules
- [ ] Modèles Pydantic pour tous les inputs critiques
- [ ] Config YAML validée par Pydantic
- [ ] Logging structuré (structlog ou équivalent)
- [ ] Hiérarchie d'exceptions custom
- [ ] Interface `InferenceEngine` abstraite définie
- [ ] Seeds gérés uniformément
- [ ] Couverture tests ≥ 80%
- [ ] Zero `print()` restant dans `src/`
- [ ] Zero valeur hardcodée dans `src/`
- [ ] Documentation des interfaces publiques (docstrings)
- [ ] Type hints à 100% sur `src/` (`mypy --strict` passe)

---

**➡️ Prochaine étape** : `04_ENTRAINEMENT_SFT.md`
