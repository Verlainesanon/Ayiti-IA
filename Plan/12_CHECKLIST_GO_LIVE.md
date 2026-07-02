# 12 — CHECKLIST GO-LIVE (LA DERNIÈRE PORTE AVANT LA PRODUCTION)

> **Règle d'or** : Si **UN SEUL** point n'est pas coché, tu ne mets pas en production. Point.

Cette checklist est la garante que tu ne livres pas un système fragile qui va s'effondrer, blesser des utilisateurs, ou entraîner des poursuites.

---

## 🟢 1. TECHNIQUE / CODE

- [ ] Tous les tests unitaires passent (`pytest tests/unit/ -v`)
- [ ] Tous les tests d'intégration passent
- [ ] Test E2E passe (mini-pipeline complet)
- [ ] Couverture de code ≥ 80% (globale), ≥ 95% (guardrails)
- [ ] `mypy --strict src/ayiti_ai/` sans erreurs
- [ ] `ruff check .` sans erreurs
- [ ] `bandit -r src/` sans High/Critical
- [ ] Aucun `TODO` critique restant
- [ ] Aucun `print()` dans le code de production
- [ ] Aucune valeur secrète en dur (scan `gitleaks`)
- [ ] Version du package fixée : `pyproject.toml` = tag Git = image Docker
- [ ] CHANGELOG.md à jour avec les changements de la release

## 🟢 2. MODÈLE

- [ ] Modèle final entraîné avec la config figée (config archivée)
- [ ] Merge LoRA + base réalisé et testé
- [ ] Quantizations produites (fp16 + AWQ + GGUF Q4_K_M)
- [ ] Hash SHA-256 de chaque artefact modèle noté
- [ ] Métadonnées `model_registry.json` mises à jour
- [ ] Test de chargement du modèle réussi sur environnement propre
- [ ] Test de génération sur 20 prompts variés → réponses cohérentes
- [ ] Pas de régression vs version précédente sur benchmarks

## 🟢 3. ÉVALUATION

- [ ] Rapport d'éval complet disponible : `results/eval/v1.0.0/report.md`
- [ ] BLEU sur `general_ht` ≥ seuil cible (défini S4)
- [ ] chrF sur `general_ht` ≥ 45
- [ ] BERTScore sur `general_ht` ≥ 0.80
- [ ] LLM-judge global ≥ 4.0/5
- [ ] Évaluation humaine ≥ 3.8/5 (min 3 évaluateurs)
- [ ] Win rate ≥ 60% vs version précédente
- [ ] Corrélation inter-évaluateurs humains ≥ 0.6 (kappa)
- [ ] Rapport d'analyse d'erreurs (worst 20) rédigé

## 🟢 4. SÉCURITÉ / GUARDRAILS

- [ ] Threat model finalisé et daté
- [ ] Toutes les couches guardrails actives (L1 à L6)
- [ ] Red team suite ≥ 300 attaques
- [ ] Taux de PASS ≥ 99% sur hard_bans
- [ ] Taux de PASS ≥ 95% sur soft_flags
- [ ] Aucune fuite PII sur benchmark contrôlé
- [ ] Détection prompt injection testée sur 50 attaques
- [ ] Kill switch testé (`safe_only` et `shutdown`)
- [ ] Rate limiting effectif (test de charge)
- [ ] Auth par API Key fonctionnelle
- [ ] HTTPS avec certificat valide > 30 jours
- [ ] Bandit + `pip-audit` : 0 vulnérabilité High/Critical
- [ ] Secrets rotation planifiée
- [ ] Blocklist reviewée dans les 7 derniers jours

## 🟢 5. INFRASTRUCTURE

- [ ] Docker images buildées, taguées, poussées au registry
- [ ] Kubernetes manifests / docker-compose testés
- [ ] Healthcheck `/health` répond en < 200ms
- [ ] Readiness `/ready` fiable (modèle vraiment chargé)
- [ ] Autoscale configuré (min/max replicas)
- [ ] Load balancer et SSL terminaison OK
- [ ] Redis cache opérationnel
- [ ] Postgres migrations appliquées, backups actifs
- [ ] Vector DB (si RAG) synchronisé et indexé
- [ ] Object storage backup automatique
- [ ] Test de restauration réussi (< 90 jours)
- [ ] Deployment Blue/Green ou Canary opérationnel

## 🟢 6. PERFORMANCE

- [ ] Test de charge passé (100 utilisateurs concurrents)
- [ ] Latence p50 sous cible
- [ ] Latence p95 sous cible
- [ ] Latence p99 tolérable
- [ ] TTFT < 1.5s
- [ ] Throughput > 20 tokens/sec/user
- [ ] GPU utilization > 70% en charge
- [ ] Aucun OOM sur benchmark stress
- [ ] Cold start < 30s
- [ ] Warm-up automatique au démarrage

## 🟢 7. MONITORING & OBSERVABILITÉ

- [ ] Prometheus scrape tous les services
- [ ] Grafana dashboards en place (5 minimum)
- [ ] Alertes P1/P2/P3 configurées
- [ ] Alertes testées (déclenchement volontaire)
- [ ] Logs structurés JSON collectés (Loki/ELK)
- [ ] Aucune PII dans les logs (audit passé)
- [ ] Tracing OpenTelemetry actif
- [ ] Feedback endpoint fonctionnel
- [ ] Dashboard business en place
- [ ] Rétention logs conforme (7j détail, 90j agrégé)

## 🟢 8. DONNÉES & COMPLIANCE

- [ ] Toutes les données ont une licence documentée
- [ ] Datacard publiée
- [ ] Modelcard publiée
- [ ] Registre RGPD-like des traitements complet
- [ ] Consentements documentés pour contributeurs
- [ ] Politique d'anonymisation appliquée
- [ ] Chiffrement au repos (données brutes + backups)
- [ ] Chiffrement en transit (TLS 1.3 partout)
- [ ] DPO ou responsable données désigné
- [ ] Procédure d'exercice des droits (accès, suppression) documentée

## 🟢 9. DOCUMENTATION PUBLIQUE

- [ ] README.md à jour, professionnel
- [ ] Documentation API (OpenAPI) publiée
- [ ] Guide utilisateur (WebUI) publié
- [ ] Guide développeur SDK publié
- [ ] Modelcard sur HF Hub (si publié)
- [ ] Datacard sur HF Hub (si publié)
- [ ] CHANGELOG.md à jour
- [ ] LICENSE / NOTICE / CITATION.cff présents
- [ ] Blog post d'annonce rédigé
- [ ] FAQ rédigée

## 🟢 10. LÉGAL & COMMUNICATION

- [ ] Terms of Service publiés (ht/fr/en)
- [ ] Privacy Policy publiée (ht/fr/en)
- [ ] Cookie Policy publiée (si applicable)
- [ ] Politique d'usage acceptable (AUP) publiée
- [ ] Contact abuse / signalement publié
- [ ] Contact support publié
- [ ] Adresse `security@` fonctionnelle
- [ ] Adresse `privacy@` fonctionnelle
- [ ] Registre légal du projet à jour (entité, adresse, RCS/RIB)
- [ ] Assurance responsabilité civile souscrite (si applicable)
- [ ] Approbation comité éthique obtenue et documentée

## 🟢 11. OPÉRATIONS

- [ ] Runbooks écrits pour Top 5 incidents
- [ ] Rotation on-call définie (même solo, plage horaire couverte)
- [ ] Canal de communication crise (Discord / Slack dédié)
- [ ] Contact escalade (juriste, expert cloud) accessible
- [ ] Procédure rollback modèle testée
- [ ] Procédure rollback code testée
- [ ] Sauvegarde configurations dans Git
- [ ] Post-mortem template prêt

## 🟢 12. UTILISATEUR

- [ ] Onboarding fluide (< 3 clics pour tester)
- [ ] Disclaimer visible ("IA en bêta, peut se tromper")
- [ ] Feedback mechanism visible (thumbs)
- [ ] Signalement de contenu accessible
- [ ] Explication de ce qui est possible / impossible
- [ ] Support répondant sous 48h (bêta)
- [ ] Multi-langue (ht/fr/en) sur toute UI
- [ ] Accessibilité de base (contraste, alt text, clavier)
- [ ] Mobile-friendly

---

## 🔴 CRITÈRES D'ARRÊT (STOP IMMÉDIAT)

Ne pas mettre en production si **UN SEUL** de ces points est vrai :

- ❌ Guardrails ont laissé passer une attaque catégorie hard_ban lors du dernier test
- ❌ Fuite PII avérée (même mineure)
- ❌ Régression majeure vs version précédente
- ❌ Test de charge échoue < 50 utilisateurs concurrents
- ❌ Aucun kill switch fonctionnel
- ❌ Backup non testé récemment
- ❌ Documentation légale absente
- ❌ Aucun contact support / abuse joignable

---

## 📋 GO/NO-GO MEETING

Réunion formelle avant chaque release (même solo).

Documente dans `docs/go-live/{version}_decision.md` :

```markdown
# Go-Live Decision: Ayiti-AI v1.0.0

## Date : 2026-XX-XX
## Présents : {noms}

## Checklist status
- Total items: 120
- Cochés : X
- Non cochés : Y (liste)
- Bloqueurs : Z

## Risques identifiés
1. ...
2. ...

## Plan de mitigation
- ...

## Décision : GO / NO-GO / GO conditionnel
Motif :

## Actions post go-live (J+1, J+7, J+30)
- ...

## Signature responsable projet : ______
```

---

## 🎯 POST GO-LIVE (J+0 à J+30)

Une fois live, tu n'as pas fini. Tu commences.

### J+0 (jour du lancement)
- Monitoring actif toute la journée
- Réponse aux 20 premiers utilisateurs personnellement
- Note tous les bugs rencontrés
- Vérifie que les métriques suivent le trend attendu

### J+1
- Post-mortem lancement rédigé
- Bugs P0 corrigés (hotfix release si nécessaire)
- Feedback initial synthétisé

### J+7
- Rétrospective première semaine
- Roadmap v1.1 initiée sur base des retours
- Métriques d'usage analysées
- Communication update publiée

### J+30
- Rapport d'usage 30 jours
- Rétention utilisateurs mesurée
- Ajustements guardrails selon comportements observés
- Plan version suivante finalisé

---

## 💬 MESSAGE FINAL

Tu es sur le point de lancer une **IA souveraine haïtienne**. C'est rare. C'est important. C'est symbolique.

Ce qui compte ce jour-là n'est pas :
- Le buzz Twitter
- Le nombre de likes
- La comparaison à ChatGPT

Ce qui compte :
- **Que le premier utilisateur réel** obtienne une réponse utile en créole naturel
- **Que rien de dangereux** ne sorte de ton système
- **Que le projet soit maintenable** sur 12 mois, pas 12 jours
- **Que tu aies documenté honnêtement** les limites (Modelcard)
- **Que tu puisses regarder** la communauté haïtienne dans les yeux

Bon lancement. 🇭🇹

---

**FIN DU PLAN.**

Reviens périodiquement à ces 12 fichiers. Ils sont ton compas.
