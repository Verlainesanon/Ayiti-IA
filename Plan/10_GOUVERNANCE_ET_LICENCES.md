# 10 — GOUVERNANCE, ÉTHIQUE & LICENCES (LES DÉCISIONS FONDATRICES)

> **Vérité inconfortable** : Un projet d'IA sans gouvernance claire finit par être poursuivi, boycotté, ou piloté par ses erreurs. Ces décisions sont **plus importantes que le code**.

---

## 10.1 QUESTIONS FONDATRICES (À TRANCHER MAINTENANT)

Assieds-toi et réponds par écrit à chaque question dans un document `docs/governance/foundational_decisions.md`. Ne code plus tant que ce n'est pas fait.

1. **À qui appartient Ayiti-AI ?** Personne physique ? Association ? Entreprise ? Coopérative ? Fondation ?
2. **Quelle est la juridiction du projet ?** Haïti ? France (RGPD) ? USA ? Autre ?
3. **Quelle licence pour le CODE ?** Apache 2.0, MIT, AGPL, propriétaire ?
4. **Quelle licence pour le MODÈLE ?** CC-BY-4.0, Apache 2.0, custom "Ayiti License", RAIL ?
5. **Quelle licence pour les DONNÉES ?** CC-BY-SA, CC0, propriétaire non-partageable ?
6. **Modèle économique ?** 100% gratuit ? Freemium ? Subscription ? Sponsors ?
7. **Politique de contributions externes ?** Ouvert PR ? CLA (Contributor License Agreement) ?
8. **Politique de partage des données brutes ?** Ouvertes, semi-ouvertes, fermées ?
9. **Qui décide quoi ?** Toi seul ? Comité ? Vote ?
10. **Quel est le "kill switch éthique" ?** Sous quelles conditions on arrête le projet ?

Ces décisions sont **irréversibles ou coûteuses à changer**. Prends le temps.

---

## 10.2 LICENCE DU CODE

### 10.2.1 Options

| Licence | Usage commercial autorisé ? | Doit rester open source ? | Choix stratégique |
|---------|-----|-----|-----|
| **MIT** | ✅ | ❌ | Ouverture max, adoption max |
| **Apache 2.0** | ✅ | ❌ | Comme MIT + protection brevets — recommandé |
| **GPL-3.0** | ✅ | ✅ (viral) | Force open source |
| **AGPL-3.0** | ✅ | ✅ (même via SaaS) | Protège contre appropriation SaaS |
| **Propriétaire** | selon toi | selon toi | Contrôle total, ferme la communauté |

**Recommandation défaut** : **Apache 2.0** — pragmatique, protège tes brevets, ouvre l'écosystème.

Si tu veux empêcher qu'une big tech reprenne ton code sans rendre : **AGPL-3.0**.

### 10.2.2 Fichier LICENSE

À la racine du repo, texte complet de la licence + un fichier `NOTICE` mentionnant :
- Copyright (année, entité)
- Contributeurs majeurs
- Dépendances tierces et leurs licences

---

## 10.3 LICENCE DU MODÈLE (SPÉCIFIQUE ML)

Un modèle IA n'est pas juste "du code". Les licences classiques ne sont pas parfaites.

### 10.3.1 Options spécifiques IA

| Licence | Restrictions d'usage ? | Recommandée pour Ayiti ? |
|---------|-----|-----|
| **Apache 2.0** | Aucune | Compatible mais permissive |
| **CC-BY-4.0** | Attribution requise | Standard académique |
| **CC-BY-SA-4.0** | Attribution + share-alike | Force les dérivés à rester ouverts |
| **OpenRAIL-M** | Restrictions d'usage (pas de désinfo, arme, etc.) | Bon compromis |
| **Llama 2/3 Community License** | Restrictions commerciales | Non — trop restrictive |
| **Custom "Ayiti License"** | À définir | Réservé si vraiment nécessaire |

**Recommandation** :
- Code : **Apache 2.0**
- Modèle : **OpenRAIL-M** (bloque les usages nuisibles listés explicitement)
- Données publiées : **CC-BY-SA-4.0** (attribution + partage sous mêmes conditions)

### 10.3.2 Cas Qwen2.5

Le modèle de base Qwen2.5 est sous **Apache 2.0**. Ton fine-tune peut être publié sous une licence égale ou plus restrictive, mais tu dois **conserver l'attribution** à Alibaba.

Documente dans `NOTICE` et `docs/model-card.md`.

---

## 10.4 LICENCE ET PROVENANCE DES DONNÉES

Chaque source de données de ton training set doit avoir une licence claire. Documente dans `docs/data-card.md` :

| Source | Licence | Compatible commercial ? | Attribution requise ? |
|--------|---------|-------------------------|-----------------------|
| Écriture manuelle interne | Ta propriété | ✅ | Non |
| Wikipedia HT | CC-BY-SA | ✅ | ✅ |
| Corpus universitaire X | À vérifier | ? | ? |
| Presse haïtienne (scraping) | ⚠️ | ❌ sans accord | ✅ |
| Génération LLM externe | Selon ToS | Variable | Selon |

**Règle absolue** : ne pas mélanger licences incompatibles. Une source viralement partageable (SA) "contamine" ton dataset.

### 10.4.1 Génération synthétique et licences

- **OpenAI GPT-4** : Terms of Use interdisent de créer un modèle concurrent d'OpenAI avec ses sorties. Zone grise pour "modèle non-concurrent". Consulte un juriste.
- **Claude (Anthropic)** : ToS similaires.
- **Mistral / Llama** : plus permissifs mais lis les ToS de leur API.
- **Modèles open weights runs par toi** : aucune restriction généralement.

**Pour être safe** : utilise pour synthétique un modèle que tu fais tourner toi-même (Mistral, Llama, Qwen) plutôt qu'API commerciale.

---

## 10.5 SOUVERAINETÉ DES DONNÉES

Le mot "souverain" dans "Ayiti-AI" implique :

### 10.5.1 Stockage

- Données brutes hébergées idéalement en Haïti ou dans les Caraïbes
- À défaut : dans une juridiction qui respecte la souveraineté haïtienne (pas les USA sous CLOUD Act pour données sensibles)
- Chiffrement au repos (AES-256) et en transit (TLS 1.3)

### 10.5.2 Contrôle d'accès

- Aucun collaborateur externe n'a accès aux données brutes non anonymisées
- Journal d'audit de tout accès
- Politique de dé-provisioning stricte

### 10.5.3 Consentement

Si des données proviennent de contributeurs haïtiens :
- Formulaire de consentement clair (en créole, français, anglais)
- Droit de retrait sans condition
- Droit à l'oubli (`article 17 RGPD` par analogie)

---

## 10.6 PROTECTION DES DONNÉES PERSONNELLES

### 10.6.1 Cadre légal

- **Haïti** : la loi sur la protection des données personnelles est en évolution. À vérifier avec un juriste local.
- **Union Européenne** : si tu sers des utilisateurs UE → **RGPD** s'applique.
- **États-Unis** : pas de loi fédérale unifiée, mais CCPA (Californie), autres États.

**Approche minimaliste sûre** : appliquer RGPD comme standard, il est plus strict que la plupart.

### 10.6.2 Principes à implémenter

1. **Minimisation** : ne collecte que le strict nécessaire
2. **Finalité** : usage limité à ce qui est déclaré
3. **Consentement explicite** : opt-in, pas opt-out
4. **Droit d'accès, rectification, suppression, portabilité**
5. **Notification** en cas de fuite (72h)
6. **Registre des traitements** (obligatoire RGPD)
7. **DPO (Data Protection Officer)** désigné si volume important

### 10.6.3 Documents publics obligatoires

- **Privacy Policy** en trois langues (ht/fr/en)
- **Terms of Service**
- **Cookie Policy** (si WebUI)
- **Politique d'usage acceptable (AUP)**

Templates de base disponibles chez Termly, iubenda — **mais fais reviewer par un juriste**.

---

## 10.7 ÉTHIQUE (LES QUESTIONS DIFFICILES)

### 10.7.1 Comité éthique

Constitue un **comité éthique consultatif** de 3-5 personnes :
- Un linguiste créoliste
- Un juriste
- Un enseignant / éducateur
- Un membre de la société civile
- (Optionnel) Un membre d'une organisation internationale

Rôle : consulté sur décisions sensibles, publie un avis annuel.

### 10.7.2 Biais et équité

Documente les biais **connus** de ton modèle :
- Biais dialectal (créole capois vs port-au-princien)
- Biais de genre dans les données (proportion homme/femme)
- Biais politique (sources presse orientées ?)
- Biais religieux (contenus vaudou vs catholique vs protestant)
- Sous-représentation des zones rurales

**Mesure-les** régulièrement et publie les résultats dans `docs/model-card.md`.

### 10.7.3 Usages proscrits (à écrire dans la licence OpenRAIL)

Non-exhaustif :
- Génération de désinformation politique
- Usurpation d'identité
- Contenus incitant à la haine ethnique/religieuse
- Manipulation électorale
- Fraude financière
- Contenus sexuels non consentis
- Prise de décision automatisée dans domaines critiques (médical, judiciaire, prêts) sans humain

### 10.7.4 Kill switch éthique

Sous quelles conditions **arrêter le projet** ? Décide **maintenant**, pas quand la crise arrive :
- Preuve d'utilisation pour propagande politique massive
- Fuite majeure de données personnelles
- Décision judiciaire
- Perte de contrôle sur les guardrails

Documente le processus décisionnel.

---

## 10.8 COMMUNAUTÉ ET CONTRIBUTIONS

### 10.8.1 CONTRIBUTING.md

Doit contenir :
- Comment cloner et setup
- Conventions de code (linter)
- Conventions de commit (Conventional Commits recommandé)
- Processus de PR (review, tests requis)
- Code de conduite (référence à `CODE_OF_CONDUCT.md`)
- CLA (Contributor License Agreement) si tu en veux un

### 10.8.2 Contributor License Agreement (CLA)

Si le projet vise commercialisation future :
- CLA individual + corporate (templates Apache CLA)
- Signature obligatoire avant merge de PR
- Outil : CLA Assistant (GitHub App)

Si projet 100% communautaire : peut être skipped.

### 10.8.3 Code of Conduct

Adopte le **Contributor Covenant 2.1** ou équivalent. Traduit-le en créole (**un geste symbolique fort**).

---

## 10.9 MODEL CARD ET DATA CARD (HUGGINGFACE STANDARD)

À chaque release publique du modèle :

### 10.9.1 `docs/model-card.md` (format HF)

- Description
- Usage prévu et hors-scope
- Limitations connues
- Biais et considérations éthiques
- Données d'entraînement (résumé)
- Métriques d'évaluation
- Émissions carbone estimées (via `codecarbon`)
- Licence
- Comment citer

### 10.9.2 `docs/data-card.md` (format HF)

- Composition
- Sources détaillées
- Processus de collecte
- Annotation (qui, comment)
- Limitations
- Distributions (langues, catégories)
- Considérations éthiques
- Licence

**C'est la transparence qui donne la légitimité.**

---

## 10.10 CITATIONS ET ATTRIBUTION

- Fichier `CITATION.cff` à la racine (format Citation File Format)
- BibTeX prêt à copier dans le README
- Encourage les usages académiques

---

## 10.11 SÉCURITÉ RESPONSIBLE DISCLOSURE

Fichier `SECURITY.md` :
- Comment reporter une vulnérabilité (email dédié : `security@ayiti-ai.ht` par exemple)
- SLA de réponse (48h)
- Politique de disclosure (90 jours standard)
- Hall of fame des chercheurs (reconnaissance)

---

## 10.12 CHECKLIST GOUVERNANCE

- [ ] `foundational_decisions.md` rédigé et validé
- [ ] Licence code choisie et fichier `LICENSE` à la racine
- [ ] Licence modèle choisie et publiée
- [ ] Licence données choisie et publiée
- [ ] Datacard rédigée
- [ ] Modelcard rédigée
- [ ] Privacy Policy publiée en ht/fr/en
- [ ] Terms of Service publiés
- [ ] Comité éthique constitué
- [ ] CONTRIBUTING.md rédigé
- [ ] CODE_OF_CONDUCT.md rédigé
- [ ] SECURITY.md rédigé
- [ ] Registre des traitements RGPD-like initié
- [ ] Contrats/accords formalisés avec contributeurs de données
- [ ] Assurance responsabilité civile envisagée (à partir de la bêta publique)

---

## 10.13 ERREURS À NE JAMAIS COMMETTRE

1. **Publier sans licence claire** → personne ne saura ce qu'il peut faire
2. **Mélanger des licences incompatibles** → contamination virale = projet mort
3. **Utiliser du scraping massif sans licence** → poursuite garantie
4. **Ne pas anonymiser les logs** → violation RGPD → amendes lourdes
5. **Se dire "on verra la gouvernance plus tard"** → tard = trop tard
6. **Ignorer les biais dans la data card** → perte de crédibilité académique
7. **Utiliser GPT-4 pour synthétique sans lire les ToS** → risque contractuel

---

**➡️ Prochaine étape** : `11_ROADMAP_12_SEMAINES.md`
