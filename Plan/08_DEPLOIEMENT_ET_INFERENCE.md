# 08 — DÉPLOIEMENT & INFÉRENCE (DU MODÈLE À L'UTILISATEUR)

> **Objectif** : Servir ton modèle de manière fiable, rapide, économique, avec une expérience utilisateur soignée.

---

## 8.1 STRATÉGIE DE DÉPLOIEMENT

Tu vas déployer sur **plusieurs environnements progressivement** :

| Phase | Cible | Public | Infra |
|-------|-------|--------|-------|
| **Alpha interne** | Toi + équipe | 5-10 users | Colab / laptop |
| **Bêta fermée** | Testeurs invités | 50-100 users | Petit VPS + GPU |
| **Bêta publique** | Sur invitation | 500-2000 users | Cloud GPU dedicated |
| **Production** | Ouverte | Public | Multi-région, autoscale |

Ne saute pas les étapes. Chaque phase révèle des problèmes uniques.

---

## 8.2 EXPORT DU MODÈLE (POST-TRAINING)

### 8.2.1 Étapes

1. **Merge LoRA + base** :
   - `PeftModel.merge_and_unload()`
   - Produit un modèle complet (~3 GB pour 1.5B)
2. **Quantization pour serving** :
   - **Développement** : bf16/fp16 (fidélité max)
   - **Production CPU** : GGUF Q4_K_M ou Q5_K_M (via llama.cpp)
   - **Production GPU** : AWQ 4-bit ou GPTQ 4-bit
3. **Vérification post-quantization** :
   - Re-évaluer sur mini-benchmark
   - Perte acceptable : < 5% sur BLEU/ROUGE
4. **Versionnage** :
   - Tag Git : `v1.0.0-model`
   - Push checkpoint sur HF Hub (privé) ou S3
   - `models/registry.json` avec métadonnées

### 8.2.2 Formats à produire

Pour un release complet :
- `ayiti-ai-v1.0-fp16/` (HF format complet)
- `ayiti-ai-v1.0-awq/` (GPU serving)
- `ayiti-ai-v1.0.Q4_K_M.gguf` (CPU serving via llama.cpp)
- `ayiti-ai-v1.0-lora/` (adaptateurs seuls, pour recherche)

---

## 8.3 MOTEUR D'INFÉRENCE (CHOIX)

| Moteur | Cas d'usage | Perf | Complexité |
|--------|------------|------|-----------|
| **HF Transformers `pipeline`** | Prototype, dev | Faible | Très basse |
| **HF `TextGenerationInference` (TGI)** | Prod simple | Bonne | Moyenne |
| **vLLM** | Prod haut débit | Excellente | Moyenne |
| **llama.cpp / ollama** | Edge, CPU, offline | Bonne | Basse |
| **NVIDIA Triton + TensorRT-LLM** | Ultra-perf entreprise | Top | Élevée |

**Recommandation par phase** :
- Alpha/Bêta fermée : **HF Transformers** dans FastAPI
- Bêta publique : **vLLM** (batching + PagedAttention → 10x throughput)
- Edge/offline : **llama.cpp** avec GGUF Q4_K_M

---

## 8.4 API REST (FastAPI)

### 8.4.1 Endpoints à exposer

```
POST /v1/chat/completions       # style OpenAI-compatible
POST /v1/completions            # legacy
GET  /v1/models                 # liste des modèles disponibles
GET  /health                    # healthcheck (liveness)
GET  /ready                     # readiness (modèle chargé ?)
GET  /metrics                   # Prometheus
POST /v1/feedback               # feedback utilisateur (thumbs up/down)
```

### 8.4.2 Schéma requête `/chat/completions`

Compatible OpenAI (permet de réutiliser les SDK existants) :

```json
{
  "model": "ayiti-ai-v1.0",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "temperature": 0.7,
  "max_tokens": 512,
  "top_p": 0.9,
  "stream": false,
  "language_hint": "ht",
  "use_rag": false
}
```

### 8.4.3 Streaming (SSE)

Indispensable pour UX moderne. `stream: true` renvoie du Server-Sent Events chunk par chunk. Implémente via `StreamingResponse` FastAPI.

### 8.4.4 Sécurité API

- Auth : API Keys (header `Authorization: Bearer <key>`)
- HTTPS obligatoire (Let's Encrypt via Caddy/Traefik)
- CORS strict (whitelist domaines)
- Body size limit (256 KB)
- Timeout 30s max
- Rate limiting par clé
- Logging structuré

---

## 8.5 INTERFACES UTILISATEUR

### 8.5.1 WebUI simple

- **Streamlit** (le plus rapide à prototyper)
- Ou **Gradio** (idéal pour démos ML)
- Ou **Next.js + shadcn/ui** (pro, personnalisable)

Fonctions essentielles :
- Chat avec historique
- Choix de langue (ht/fr/en)
- Toggle RAG
- Feedback (thumbs up/down + commentaire)
- Copie/partage de réponses
- Disclaimer permanent

### 8.5.2 Chatbot messagerie

Où sont tes utilisateurs haïtiens ? Sur **WhatsApp** et **Facebook Messenger** massivement. Envisage :

- **WhatsApp Business API** (via Twilio, 360dialog)
- **Messenger** (Meta Graph API)
- **Telegram** (le plus simple, bot API gratuit)

Développe d'abord Telegram (facile) → puis WhatsApp (impact max HT).

### 8.5.3 SDK et intégration

Fournis :
- Client Python (`pip install ayiti-ai-client`)
- Client JS/TS (`npm install ayiti-ai`)
- Documentation OpenAPI (auto-générée par FastAPI)

---

## 8.6 INFRASTRUCTURE

### 8.6.1 Options d'hébergement (par coût croissant)

| Option | Coût/mois | GPU | Convient à |
|--------|-----------|-----|------------|
| **Local (ta machine)** | 0 | Optionnel | Dev, démo |
| **HuggingFace Spaces** | 0-10$ | CPU / A10G | Démo publique |
| **Fly.io / Railway** | 5-50$ | CPU only | Bêta CPU-inférence GGUF |
| **Runpod Serverless** | pay-per-request | GPU | Bêta et prod (petit volume) |
| **Lambda Labs on-demand** | 1-1.5$/h | A100 | Prod stable |
| **AWS/GCP GPU** | Variable | Divers | Prod scale |
| **Serveur souverain (VPS local HT/Caraïbes)** | Variable | Selon | Idéal politiquement |

**Souveraineté** : si le projet est vraiment "IA souveraine haïtienne", cherche un hébergeur en Haïti ou dans les Caraïbes (Anguilla, Dominique...). C'est cohérent avec la mission.

### 8.6.2 Architecture cible (prod)

```
[Cloudflare]  ← CDN + DDoS protection
     ↓
[Load Balancer]  ← Traefik/nginx
     ↓
[API Gateway]  ← FastAPI (auth, rate limit)
     ↓
[Inference workers]  ← vLLM sur GPU, autoscale 1-N
     ↓
[Redis]  ← cache réponses + sessions
     ↓
[Postgres]  ← users, feedback, logs applicatifs
     ↓
[Object storage S3]  ← modèles, logs longs
```

### 8.6.3 Containerisation

- Chaque service dans un container Docker
- **`docker-compose.yml`** pour dev/bêta
- **Kubernetes (K8s)** ou **Nomad** pour prod scale
- Registry privé (GHCR, ECR, Docker Hub privé)

---

## 8.7 PERFORMANCE ET LATENCE

### 8.7.1 Cibles

| Métrique | Cible bêta | Cible prod |
|----------|-----------|-----------|
| **Time-to-First-Token (TTFT)** | < 2s | < 800ms |
| **Tokens/sec (throughput)** | > 20 | > 50 |
| **Latence p95 (réponse complète)** | < 8s | < 4s |
| **Disponibilité** | > 95% | > 99.5% |
| **Concurrent users supportés** | 5-10 | 100+ |

### 8.7.2 Optimisations

1. **Continuous batching** (vLLM natif)
2. **KV cache** partagé entre requêtes
3. **Speculative decoding** (avec un draft model plus petit)
4. **Prompt caching** (préfixes système partagés)
5. **Quantization AWQ/GPTQ**
6. **Flash Attention 2**
7. **Warm-up** au démarrage (éviter cold start)

### 8.7.3 Benchmark de charge

Avant chaque release :
- **`locust`** ou **`k6`** pour simuler 10-100 users concurrents
- Mesure latence, throughput, taux d'erreur
- Documente les résultats dans `docs/perf/`

---

## 8.8 GESTION DES VERSIONS (SEMVER)

Modèle et code suivent SemVer :

- **MAJOR** : changement d'architecture ou breaking API
- **MINOR** : nouveau training, améliorations mesurables
- **PATCH** : hotfix, ajustement config

Tag Git : `v1.2.3` → CI build image Docker `ayiti-ai:1.2.3`.

Toujours **au moins 2 versions coexistent** en prod (canary deployment).

---

## 8.9 CANARY & BLUE/GREEN DEPLOYMENT

### 8.9.1 Canary

Nouveau modèle → 5% du trafic → observe métriques → progressive à 25%, 50%, 100%.

Rollback automatique si :
- Taux d'erreur augmente > 2%
- Latence p95 augmente > 30%
- Feedback négatif > 20%

### 8.9.2 Blue/Green

Deux stacks identiques (blue = live, green = new). Bascule DNS/LB. Rollback instantané possible.

Choix selon ta maturité opérationnelle. Canary est plus doux.

---

## 8.10 COÛT D'INFRA (ESTIMATIONS RÉALISTES)

Pour 100 utilisateurs actifs/jour, ~5000 requêtes/jour :

| Composant | Solution | Coût mensuel USD |
|-----------|----------|------------------|
| GPU inference (A10G 24/7) | Runpod ou Lambda | 250-400 |
| API server (2 vCPU / 4GB) | Fly.io | 20-40 |
| Vector DB (Qdrant) | Self-host | 15 (VPS) |
| Redis (cache) | Managed | 15 |
| Postgres (users, logs) | Neon / Supabase | 25 |
| Cloudflare (CDN) | Free tier | 0 |
| Monitoring (Grafana Cloud) | Free tier | 0 |
| Object storage (S3) | Backblaze B2 | 5-10 |
| Domaine + certificats | Namecheap + Let's Encrypt | 1-2 |
| **TOTAL** | | **330-500** |

Pour économiser :
- **Serverless GPU** (Runpod Serverless, Modal, Replicate) : paie seulement à l'utilisation
- **Quantization agressive** + serveur CPU large (32 threads) peut suffire à petite échelle

---

## 8.11 EXPORT ET MODES OFFLINE

Un usage précieux du modèle en Haïti : **fonctionnement sans internet**.

Prépare une version :
- **GGUF Q4_K_M** (< 1 GB pour 1.5B)
- **Application desktop** avec `Ollama` embed ou `llama.cpp` runtime
- **Mobile** : `mlc-llm` (Android/iOS) — plus complexe

C'est un avantage stratégique énorme dans un pays où la connectivité est instable.

---

## 8.12 CHECKLIST DÉPLOIEMENT

Avant d'aller en bêta publique :

- [ ] Modèle mergé + quantizé + testé
- [ ] API OpenAI-compatible fonctionnelle
- [ ] Streaming SSE marche
- [ ] Auth par API key
- [ ] Rate limiting effectif
- [ ] HTTPS obligatoire
- [ ] Docker image < 2 GB
- [ ] WebUI publique déployée
- [ ] Bot Telegram fonctionnel
- [ ] Benchmark de charge passé (100 users concurrents)
- [ ] Latence p95 dans les cibles
- [ ] Monitoring en place (cf. fichier 09)
- [ ] Rollback plan documenté et testé
- [ ] Documentation utilisateur publiée
- [ ] Terms of Service + Privacy Policy publiés
- [ ] Contact support publié

---

**➡️ Prochaine étape** : `09_MONITORING_ET_OBSERVABILITE.md`
