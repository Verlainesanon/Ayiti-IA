# 07 — RAG & BASE DE CONNAISSANCES (RÉDUIRE LES HALLUCINATIONS)

> **Vérité** : Un modèle 1.5B n'a pas les connaissances factuelles d'un 70B. Il va halluciner sur l'histoire, la géographie, les personnages haïtiens.
>
> **Solution** : Un système RAG (Retrieval-Augmented Generation) qui injecte des faits vérifiés dans le contexte du modèle.

---

## 7.1 QUAND UTILISER RAG (ET QUAND NON)

### 7.1.1 Cas d'usage RAG

| Cas | RAG utile ? |
|-----|-------------|
| Questions factuelles précises (dates, personnes) | ✅ Oui |
| Questions culturelles complexes | ✅ Oui |
| Questions juridiques d'information | ✅ Oui |
| Recherche dans un corpus (loi, presse) | ✅ Oui |
| Conversation quotidienne | ❌ Non |
| Traduction | ❌ Non |
| Génération créative | ❌ Non |
| Réponses courtes évidentes | ❌ Non |

Idée clé : **RAG conditionnel**. Ton pipeline décide s'il applique RAG ou pas selon le prompt.

---

## 7.2 ARCHITECTURE RAG

```
[User query]
     ↓
[Query classifier] → "besoin de RAG ?" (oui/non)
     ↓ (si oui)
[Query rewriter] → reformule pour retrieval optimal (souvent en fr)
     ↓
[Embedder] → vecteur dense
     ↓
[Vector DB search] → top-k documents pertinents
     ↓
[Reranker] → top-N après re-scoring (bge-reranker-v2)
     ↓
[Context builder] → assemble contexte + citations
     ↓
[LLM Ayiti] → génère avec contexte injecté
     ↓
[Citation checker] → vérifie que sources sont bien citées
     ↓
[Réponse + citations]
```

---

## 7.3 SOURCES POUR LA BASE DE CONNAISSANCES

### 7.3.1 Priorités

1. **Constitution haïtienne** (domaine public)
2. **Wikipedia HT / FR** (article Haïti et sous-articles) — Creative Commons
3. **MENFP curricula** (si autorisation)
4. **Institut Haïtien de Statistique** (IHSI) — données publiques
5. **Ouvrages historiques du domaine public** (Ardouin, Madiou...)
6. **Presse haïtienne archivée** (avec accord ou fair use pour indexation)
7. **Corpus créoles universitaires** (avec licences)

### 7.3.2 Volume cible

- **v1** : 500-1000 documents (chunks après découpage : 10K-50K)
- **v2** : 3000-5000 documents (chunks : 100K+)

---

## 7.4 PIPELINE D'INGESTION

### 7.4.1 Extraction

Selon la source :
- **PDF** : `PyMuPDF`, `pdfplumber` (préserve la structure)
- **HTML** : `trafilatura` (extrait contenu principal, retire nav/pub)
- **Wikipedia** : API `wikitextparser` + `mwparserfromhell`
- **Scans OCR** : Tesseract (avec `-l fra+eng+hat`)

### 7.4.2 Nettoyage

- Retirer headers/footers
- Normaliser unicode (NFC)
- Détecter et taguer la langue par paragraphe (`fasttext-langid`)
- Retirer duplicatas exacts et quasi-doublons

### 7.4.3 Chunking (crucial)

- **Stratégie** : semantic chunking, pas fixed-size
- **Outil** : `langchain.text_splitter.RecursiveCharacterTextSplitter` avec séparateurs adaptés (`\n\n`, `\n`, `. `, ` `)
- **Taille** : 512 tokens par chunk, overlap 64 tokens
- **Métadonnées** par chunk :
  - `source` (URL / titre document)
  - `page` (si applicable)
  - `language` (ht/fr/en)
  - `topic` (histoire/culture/etc.)
  - `date_publication`
  - `license`

### 7.4.4 Embedding

Modèle recommandé : **`intfloat/multilingual-e5-large`** (support ht partiel via multilingue).

Alternatives :
- `BAAI/bge-m3` (excellent, multilingue, coûteux en dim)
- `intfloat/multilingual-e5-base` (plus léger)

Prefix E5 : `passage: {text}` pour docs, `query: {q}` pour requêtes.

---

## 7.5 CHOIX DE VECTOR DATABASE

| Solution | Pour | Contre |
|----------|------|--------|
| **FAISS** | Local, rapide, gratuit | Pas de méta filtering avancé, mono-machine |
| **Qdrant** | Open source, cloud/self-host, méta riches | Un peu plus lourd à opérer |
| **Weaviate** | Multi-modal, GraphQL | Complexité |
| **Milvus** | Scale extrême | Overkill pour ton volume |
| **pgvector** | Simple si Postgres déjà présent | Perf < spécialisées à grande échelle |

**Recommandation** : **Qdrant** (self-host Docker) — bon compromis features/simplicité.

---

## 7.6 RETRIEVAL

### 7.6.1 Recherche vectorielle

- Top-k=20 initial (over-fetch pour permettre reranking)
- Distance : cosine (défaut E5)
- Filtres méta : par langue, par topic

### 7.6.2 Hybrid search (fortement recommandé)

Combine :
- **Dense retrieval** (embedding) : bon pour sémantique
- **Sparse retrieval** (BM25) : bon pour termes rares, noms propres, dates

Fusion via **Reciprocal Rank Fusion (RRF)**.

### 7.6.3 Reranking

- Modèle : `BAAI/bge-reranker-v2-m3` (multilingue, léger)
- Rescore les top-20 → garde top-5
- Améliore significativement la précision

### 7.6.4 Filtres de qualité

Après reranking :
- Score minimum (ex. > 0.5 après rerank)
- Diversité (MMR : Maximum Marginal Relevance)
- Fraîcheur (pénalise docs très anciens si topic actuel)

---

## 7.7 CONSTRUCTION DU CONTEXTE

### 7.7.1 Format du prompt RAG

```
<|im_start|>system
{system_prompt_ayiti}

Ou gen aksè ak enfòmasyon anba a. Sèvi ak yo pou reponn kesyon an.
Si repons lan pa nan enfòmasyon yo, di w pa konnen.
Toujou site sous ou (ex: [1], [2]).

--- Sous ---
[1] {source_1} ({url_1})
{extract_1}

[2] {source_2} ({url_2})
{extract_2}
--- Fen sous ---
<|im_end|>
<|im_start|>user
{user_question}<|im_end|>
<|im_start|>assistant
```

### 7.7.2 Gestion de la longueur

- Fenêtre Qwen2.5-1.5B : 32K tokens (large)
- Mais **plus de contexte ≠ meilleure qualité** (perte au milieu)
- Cible : 3-5 chunks max, ~1500 tokens de contexte total
- Priorité si trop long : couper les moins pertinents

---

## 7.8 CITATIONS ET TRAÇABILITÉ

Ton modèle DOIT citer ses sources.

### 7.8.1 Injection dans le prompt

Chaque chunk arrive avec un identifiant `[1]`, `[2]`... Le modèle est entraîné (via SFT sur exemples RAG) à intégrer `[N]` dans sa réponse.

### 7.8.2 Post-processing

- Parser la réponse pour extraire les `[N]`
- Retourner à l'API un objet structuré :
  ```json
  {
    "answer": "...",
    "citations": [
      {"id": 1, "source": "Wikipedia HT — Dessalines", "url": "..."},
      {"id": 2, "source": "Constitution HT 1987", "url": "..."}
    ]
  }
  ```

### 7.8.3 Interface utilisateur

Affiche les sources cliquables sous la réponse. Standard chez Perplexity/You/Bing.

---

## 7.9 ENTRAÎNEMENT DU MODÈLE À BIEN UTILISER LE RAG

Ajoute au dataset SFT une catégorie `RAG` :

- 500-1000 exemples où l'`input` contient un contexte simulé (avec `[1]`, `[2]`...)
- L'`output` cite correctement
- Inclure exemples où le contexte NE contient PAS la réponse → modèle doit dire "Mwen pa jwenn enfòmasyon sa a nan sous yo"

Sans cet entraînement, le modèle ignorera souvent le contexte.

---

## 7.10 ÉVALUATION SPÉCIFIQUE RAG

Benchmarks additionnels :

- **`eval/rag_faithfulness.jsonl`** : la réponse dit-elle uniquement ce qui est dans le contexte ?
- **`eval/rag_relevance.jsonl`** : le contexte récupéré est-il pertinent ?
- **`eval/rag_no_context.jsonl`** : modèle dit-il "je ne sais pas" quand approprié ?

Métriques dédiées :
- **Faithfulness** (fidélité) : % de claims dans la réponse supportés par le contexte (via LLM judge)
- **Answer relevance** : la réponse traite-t-elle la question ?
- **Context precision** : % des chunks retournés qui sont pertinents

Outils : **RAGAS** framework (fait exactement ça).

---

## 7.11 CACHE ET PERFORMANCE

- Cache des embeddings de queries fréquentes
- Cache des top-k pour queries identiques (TTL 1h)
- Pré-chargement du reranker en mémoire
- Batching des embeddings à l'ingestion

Latence cible RAG complet : < 1.5s en plus de la génération.

---

## 7.12 MAINTENANCE DE LA BASE

- **Ré-indexation** mensuelle (nouveaux docs, corrections)
- **Éviction** des docs obsolètes/incorrects
- **Versioning** de l'index (comme les modèles)
- **Monitoring** des queries sans résultat (indique lacune de la KB)

---

## 7.13 CHECKLIST RAG

- [ ] Sources identifiées avec licences claires
- [ ] Pipeline d'ingestion automatisé (idempotent)
- [ ] Chunking sémantique en place
- [ ] Vector DB déployé et versionné
- [ ] Hybrid search (dense + sparse)
- [ ] Reranker actif
- [ ] Format de citation standardisé
- [ ] SFT inclut exemples RAG
- [ ] Évaluation RAGAS lancée
- [ ] Faithfulness ≥ 0.85
- [ ] Latence acceptable
- [ ] Monitoring queries sans résultat

---

## 7.14 QUAND SKIPPER LE RAG

Le RAG est complexe. Pour ton **MVP (S1-S8)**, tu peux le skipper.

Introduis-le à partir de **v1.0** ou **v2.0**, quand :
- Tu as constaté par éval que les hallucinations factuelles sont un problème
- Tu as un corpus de connaissances à indexer
- Tu peux consacrer 2-3 semaines à sa mise en place

---

**➡️ Prochaine étape** : `08_DEPLOIEMENT_ET_INFERENCE.md`
