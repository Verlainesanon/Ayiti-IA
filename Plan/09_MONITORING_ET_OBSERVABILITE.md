# 09 — MONITORING & OBSERVABILITÉ (VOIR CE QUI SE PASSE)

> **Loi fondamentale** : Ce qui n'est pas mesuré n'est pas géré. En production, un modèle IA a des comportements imprévus. Sans monitoring, tu es aveugle.

---

## 9.1 LES 3 PILIERS D'OBSERVABILITÉ

1. **Metrics** (quoi qui se passe) — Prometheus + Grafana
2. **Logs** (détails de chaque événement) — Loki ou ELK
3. **Traces** (parcours d'une requête à travers les services) — Jaeger / Tempo / OpenTelemetry

Chacun apporte une dimension. Les trois ensemble = observabilité complète.

---

## 9.2 MÉTRIQUES SYSTÈME

À collecter avec **Prometheus** (via `prometheus_client` en Python) :

### 9.2.1 Métriques API

- `ayiti_requests_total{endpoint, status}` — counter
- `ayiti_request_duration_seconds{endpoint}` — histogram
- `ayiti_active_requests` — gauge
- `ayiti_request_size_bytes` / `ayiti_response_size_bytes` — histogram
- `ayiti_errors_total{type}` — counter (validation, timeout, guardrail_blocked, etc.)

### 9.2.2 Métriques modèle

- `ayiti_generation_tokens_total{model_version}` — counter
- `ayiti_generation_duration_seconds` — histogram
- `ayiti_ttft_seconds` (time-to-first-token) — histogram
- `ayiti_prompt_tokens` / `ayiti_completion_tokens` — histogram
- `ayiti_gpu_memory_bytes` — gauge
- `ayiti_gpu_utilization_percent` — gauge
- `ayiti_queue_size` — gauge (attente de génération)

### 9.2.3 Métriques métier

- `ayiti_guardrail_triggered_total{layer, reason}`
- `ayiti_language_detected_total{lang}`
- `ayiti_category_predicted_total{category}`
- `ayiti_rag_activated_total`
- `ayiti_feedback_total{sentiment}` (thumbs up/down)
- `ayiti_user_sessions_active` — gauge
- `ayiti_daily_active_users` (via cron aggregate)

### 9.2.4 Métriques infra

Via `node_exporter` :
- CPU, RAM, disque, réseau
- `nvidia_gpu_exporter` : GPU util, temp, memory

---

## 9.3 LOGS STRUCTURÉS

Chaque log est un JSON avec **au minimum** :

- `timestamp` (ISO 8601 UTC)
- `level` (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `service` (api, inference, guardrail, rag)
- `event` (nom canonique en snake_case)
- `trace_id` (correlation cross-services)
- `user_id_hash` (jamais l'ID clair)
- `duration_ms` (si applicable)
- Champs métier spécifiques

### 9.3.1 Événements-clés à toujours logger

- `request.received`
- `request.completed`
- `guardrail.input_blocked` avec `reason`
- `guardrail.output_blocked` avec `reason`
- `model.generation_started` / `completed`
- `rag.retrieval` avec `n_docs`, `top_score`
- `error.*` avec stack trace
- `feedback.received`

### 9.3.2 Ce qu'il NE FAUT PAS logger

- Prompts en clair (préférer un hash + prefix 50 caractères max)
- Réponses en clair
- Emails, téléphones, noms complets
- Tokens d'authentification
- Contenu médical/juridique personnel

**RGPD friendly par design.**

### 9.3.3 Stack de collecte

- **Vector.dev** ou **Fluent Bit** : agent local qui shippe
- **Loki** : stockage logs (label-based, économique)
- **Grafana** : requêtes LogQL, alertes

---

## 9.4 TRACING DISTRIBUÉ

Avec **OpenTelemetry** :

1. Chaque requête entrante génère un `trace_id`
2. Chaque appel interne (guardrail → RAG → model → output filter) est un `span`
3. Export vers Tempo / Jaeger
4. Visualisation : timeline complète d'une requête, où le temps est passé

Utile pour :
- Identifier les goulots d'étranglement (RAG lent ? modèle lent ?)
- Débuguer des requêtes spécifiques
- Comprendre les erreurs en cascade

Instrumente FastAPI automatiquement via `opentelemetry-instrumentation-fastapi`.

---

## 9.5 DASHBOARDS GRAFANA

Crée au minimum 5 dashboards :

### 9.5.1 "Overview" (accessible équipe entière)

- Requêtes/min (7 derniers jours)
- Taux d'erreur global
- Latence p50/p95/p99
- Users actifs
- Guardrails déclenchés
- Feedback positif/négatif

### 9.5.2 "Model performance"

- TTFT
- Tokens/sec
- GPU util
- Queue depth
- Distribution des longueurs de prompt/réponse

### 9.5.3 "Safety & Guardrails"

- Refus par catégorie
- Attaques détectées (input filter)
- Toxicité moyenne des sorties
- Escalades manuelles

### 9.5.4 "Usage & Product"

- Langue de requête
- Catégorie de topic
- Sessions par heure
- Rétention 1j/7j/30j
- Feedback détaillé

### 9.5.5 "Infra & Cost"

- Coût GPU/jour
- Coût par requête
- Utilisation par instance
- Erreurs infra (5xx)

---

## 9.6 ALERTES (PagerDuty / OpsGenie / Slack)

Configure des alertes graduées.

### 9.6.1 Alertes P1 (réveiller quelqu'un la nuit)

- API down (health check fail > 2 min)
- Taux d'erreur 5xx > 5% pendant 5 min
- Aucune requête reçue depuis 10 min (traffic effondré)
- GPU OOM répétés
- Guardrails critiques désactivés (via feature flag)

### 9.6.2 Alertes P2 (heures ouvrées)

- Latence p95 > 2× cible pendant 15 min
- Taux de refus guardrails > 20% (soit attaques massives soit modèle cassé)
- Feedback négatif > 30% sur les 100 dernières requêtes
- Disque > 85%
- Certificat SSL < 15 jours d'expiration

### 9.6.3 Alertes P3 (revue matinale)

- Latence dégradée
- Métriques métier anormales (chute langues ht ou fr)
- Nouveau type d'erreur détecté

---

## 9.7 FEEDBACK LOOP

Le monitoring passif ne suffit pas. Collecte du feedback **utilisateur** :

### 9.7.1 Mécanismes

- **Thumbs up/down** après chaque réponse
- **Champ commentaire libre** optionnel
- **Signalement** ("Signal réponse problématique")
- **Suggestion de correction** ("Cette réponse est fausse. Voici la bonne :")

### 9.7.2 Traitement

- Stockage en base (Postgres)
- Tableau de bord dédié
- Review hebdomadaire par un humain
- Tri des cas problématiques → ajout au dataset SFT / red team suite

**Sans ce loop, ton modèle ne s'améliore pas après le déploiement.**

---

## 9.8 DÉTECTION DE DRIFT

### 9.8.1 Model drift

Le comportement du modèle change ? Suit :
- Distribution de longueurs de réponse
- Distribution de "temperature effective" (entropie des sorties)
- Score moyen de toxicité
- Ratio de refus

Si dérive > 20% sans changement de modèle → il se passe quelque chose (attaques ? bug ?).

### 9.8.2 Data drift

Les inputs changent ? Suit :
- Distribution de longueurs de prompt
- Distribution de langues détectées
- Distribution de topics
- Vocabulaire des tokens (via un sketch)

Si data drift majeur → besoin de réentraînement.

### 9.8.3 Concept drift

Les faits deviennent obsolètes ? Ex : constitution modifiée, personnage décédé, monnaie dévaluée.

- Signalements utilisateurs = 1er signal
- Audits périodiques (semi-annuels) de la KB RAG
- Re-collecte de données actualisées

---

## 9.9 AUDIT LOGS (COMPLIANCE)

Séparé du logging applicatif, plus strict :

- Changement de configuration système (qui, quand, quoi)
- Modifications de guardrails
- Actions admin (kill switch, ban user)
- Accès aux données personnelles
- Exports de données

**Rétention** : selon obligation légale (souvent 5 ans+).

**Immutabilité** : logs signés ou dans un système append-only (S3 Object Lock).

---

## 9.10 PLAN DE CONTINUITÉ

Documente :

### 9.10.1 Playbooks

- `docs/runbooks/api_down.md`
- `docs/runbooks/gpu_oom.md`
- `docs/runbooks/guardrail_bypass_detected.md`
- `docs/runbooks/data_leak_suspected.md`
- `docs/runbooks/model_rollback.md`

Chaque playbook : symptômes, diagnostic, actions, escalade.

### 9.10.2 Exercices (game days)

Tous les 2-3 mois, simule un incident (arrête un service exprès). Mesure temps de détection, résolution, communication.

### 9.10.3 Backups

- Modèles : réplication multi-région
- Postgres : snapshots quotidiens + PITR
- Vector DB : snapshot hebdo
- Configuration : dans Git (source of truth)

Test de **restore** trimestriel obligatoire.

---

## 9.11 CHECKLIST OBSERVABILITÉ

- [ ] Prometheus scrape tous les services
- [ ] Grafana avec 5 dashboards clés
- [ ] Logs structurés JSON partout
- [ ] Aucune PII dans les logs
- [ ] OpenTelemetry tracing actif
- [ ] Alertes P1/P2/P3 configurées et testées
- [ ] Feedback utilisateur collecté et traité
- [ ] Détection drift automatisée
- [ ] Audit logs séparés et sécurisés
- [ ] Playbooks écrits pour top 5 incidents
- [ ] Restore backup testé récemment

---

## 9.12 ANTI-PATTERNS

1. **Loguer les prompts en clair** → violation RGPD, danger PII
2. **Alertes trop bruyantes** → équipe désensibilisée, ignore les vraies
3. **Métriques sans dashboard** → data collectée mais jamais regardée
4. **Pas de traces** → tu ne sais jamais pourquoi une requête est lente
5. **Feedback collecté sans revue** → utilisateur frustré, aucune amélioration
6. **Alertes sans playbook** → panique quand ça pète

---

**➡️ Prochaine étape** : `10_GOUVERNANCE_ET_LICENCES.md`
