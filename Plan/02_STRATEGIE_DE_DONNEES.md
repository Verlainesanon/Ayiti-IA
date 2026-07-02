# 02 — STRATÉGIE DE DONNÉES (LE CŒUR DU PROJET)

> **Vérité fondamentale** : Un modèle mal entraîné sur d'excellentes données est bien meilleur qu'un modèle parfait entraîné sur des données médiocres. **Tes données valent 80% du résultat final.**
>
> **Objectif** : Atteindre **15 000 paires d'instructions validées** en créole, français et anglais, réparties selon une taxonomie claire, avec des splits reproductibles et une chaîne de qualité stricte.

---

## 2.1 CADRAGE DU DATASET

### 2.1.1 Volumes cibles

| Milestone | Volume total | Répartition ht/fr/en |
|-----------|--------------|----------------------|
| MVP (S4) | 1 000 paires | 70/20/10 |
| V1 (S8) | 5 000 paires | 60/25/15 |
| V2 (S12) | 15 000 paires | 55/30/15 |
| V3 (long terme) | 50 000+ | 50/30/20 |

Le créole reste **majoritaire** — c'est la raison d'être du projet.

### 2.1.2 Taxonomie des catégories (à figer maintenant)

Chaque paire DOIT appartenir à **une et une seule** catégorie principale. Voici la taxonomie recommandée :

| Code | Catégorie | % cible | Exemples de contenu |
|------|-----------|---------|---------------------|
| `LANG` | Langue & grammaire | 15% | Traductions, conjugaisons, orthographe créole |
| `CULT` | Culture & traditions | 15% | Vaudou, carnaval, kompa, cuisine |
| `HIST` | Histoire d'Haïti | 10% | Révolution, indépendance, personnages |
| `GEO` | Géographie | 5% | Départements, villes, climat |
| `EDU` | Éducation & savoir | 10% | Maths simples, sciences, questions scolaires |
| `SANT` | Santé (grand public) | 8% | Info préventive, JAMAIS de diagnostic |
| `AGRI` | Agriculture & environnement | 7% | Cultures locales, saisons, techniques |
| `ECON` | Économie & vie pratique | 8% | Argent, marché, coopératives, transferts |
| `DROI` | Droit citoyen (info) | 5% | Papiers, démarches, JAMAIS conseil juridique |
| `DIAL` | Dialogues quotidiens | 12% | Salutations, marché, taxi, famille |
| `PROV` | Proverbes & sagesse | 3% | Explications de proverbes créoles |
| `TECH` | Technologie & numérique | 2% | Explications de concepts |

**Règle** : chaque paire a un champ `category` obligatoire avec un de ces codes.

---

## 2.2 SCHÉMA DE DONNÉES (STRICT)

Chaque ligne JSONL DOIT respecter ce schéma. Valide-le avec Pydantic ou `jsonschema` :

```json
{
  "id": "ayiti-000001",
  "instruction": "string, obligatoire, 5-500 caractères",
  "input": "string, optionnel, contexte additionnel",
  "output": "string, obligatoire, 5-2000 caractères",
  "language": "ht | fr | en",
  "category": "LANG | CULT | HIST | ...",
  "source": "manual | translated | scraped:<domain> | synthetic:<model>",
  "quality_score": "float 0-1, rempli après revue",
  "reviewer": "string, initiales du relecteur",
  "reviewed_at": "ISO 8601 date",
  "license": "CC-BY-4.0 | CC0 | proprietary | ...",
  "tags": ["array", "de", "mots-clés"],
  "difficulty": "easy | medium | hard",
  "requires_context": false
}
```

**Champs interdits** : jamais de noms de personnes réelles non publiques, jamais de numéros de téléphone, jamais d'emails, jamais de CIN/NIF.

---

## 2.3 SOURCES DE DONNÉES (par priorité)

### 2.3.1 Sources primaires (à privilégier)

1. **Écriture manuelle par des locuteurs natifs** — qualité max, coût élevé
2. **Corpus créoles publics libres** :
   - CreoleTrans (si licence compatible)
   - Bible en créole (Domaine public pour certaines versions)
   - Manuels scolaires du MENFP (vérifier autorisation)
3. **Traduction de datasets d'instructions existants** :
   - Alpaca, Dolly, OpenAssistant → traduire vers ht avec relecture humaine

### 2.3.2 Sources secondaires (avec précaution)

4. **Scraping éthique** de sites haïtiens :
   - Presse : Le Nouvelliste, AlterPresse, Loop Haïti (vérifier ToS)
   - Wikipedia créole (`ht.wikipedia.org`)
   - Forums publics (avec anonymisation stricte)
5. **Radio/TV transcrite** (avec accord)

### 2.3.3 Sources tertiaires (à valider une par une)

6. **Génération synthétique par LLM** (GPT-4, Claude, Mistral) :
   - **JAMAIS** utilisée sans relecture humaine à 100%
   - Toujours marquée `source: synthetic:<model>`
   - Ratio max : 30% du dataset final
7. **Back-translation** : traduire fr→ht→fr pour créer des paraphrases

---

## 2.4 PROCESSUS DE COLLECTE (WORKFLOW OPÉRATIONNEL)

### 2.4.1 Rôles à définir

| Rôle | Responsabilité |
|------|---------------|
| **Collecteur** | Produit les paires brutes |
| **Réviseur linguistique** | Valide créole natif, corrige |
| **Réviseur qualité** | Vérifie schéma, doublons, catégorie |
| **Validateur final** | Approuve pour intégration au dataset |

Même en solo, tu joues **chaque rôle à un moment différent** (jamais dans la même session — biais).

### 2.4.2 Pipeline de collecte (5 étapes)

```
[1. COLLECTE]        → data/raw/inbox/<contributeur>_<date>.jsonl
      ↓
[2. VALIDATION SCHÉMA] → scripts/collect_data.py --validate (rejette si non conforme)
      ↓
[3. DÉDUPLICATION]   → hash sur (instruction, output) + fuzzy matching (RapidFuzz)
      ↓
[4. REVUE LINGUISTIQUE] → outil d'annotation (Argilla, Label Studio) OU Google Sheet
      ↓
[5. INTÉGRATION]     → data/raw/curated/YYYY-MM.jsonl (versionné DVC)
```

### 2.4.3 Outil d'annotation recommandé

**Argilla** (open source, self-hostable) :
- Interface web pour reviewer les paires
- Système de scoring intégré
- Export JSONL direct
- Compatible HuggingFace

Alternative simple : Google Sheets partagé avec validation par colonne + script d'export.

---

## 2.5 QUALITÉ DES DONNÉES (RÈGLES ABSOLUES)

### 2.5.1 Critères d'acceptation d'une paire

Une paire est **acceptée** si :
1. Créole natural (pas de "créole scolaire" francisé)
2. Orthographe conforme à l'orthographe officielle IPN (Institut Pédagogique National)
3. Longueur `output` proportionnée à `instruction` (pas de réponses monosyllabiques sauf si pertinent)
4. Pas de contenu factuel faux vérifiable
5. Pas de PII (données personnelles)
6. Pas de propos haineux, discriminatoires, sexistes
7. Registre approprié (respectueux, informatif)
8. Diversité : pas 50 variantes du même exemple

### 2.5.2 Détection automatique de problèmes

Écris un script `scripts/data_quality.py` qui détecte :

- **Doublons exacts** (hash SHA1 de `instruction+output`)
- **Doublons flous** (RapidFuzz > 85%)
- **Longueurs anormales** (percentile < 1 ou > 99)
- **Ratio créole** (via `langdetect` ou `fasttext-langid`) — flag si `ht` déclaré mais détecté `fr`
- **PII** :
  - Regex email : `\b[\w.-]+@[\w.-]+\.\w+\b`
  - Téléphone HT : `\+?509[-\s]?\d{4}[-\s]?\d{4}`
  - Regex CIN/NIF (formats haïtiens)
- **Toxicité** : passer par `detoxify` (multilingue) ou API Perspective
- **Contradictions internes** : rare mais possible

### 2.5.3 Métriques qualité à suivre (dashboard)

- Nombre total de paires par split (train/val/test)
- Distribution par catégorie
- Distribution par langue
- Distribution des longueurs (histogramme)
- Taux de rejet par étape
- Score qualité moyen (0-1)
- Diversité lexicale (type/token ratio)

---

## 2.6 SPLITS TRAIN / VAL / TEST

### 2.6.1 Ratio

- **Train** : 80%
- **Validation** : 10% (utilisé pendant l'entraînement pour early stopping)
- **Test** : 10% (JAMAIS vu par le modèle — sacré)

### 2.6.2 Stratification

Le split n'est **pas aléatoire pur**. Il est stratifié sur :
- Langue (`ht/fr/en`)
- Catégorie (LANG, CULT, ...)
- Difficulté (`easy/medium/hard`)
- Source (manuel vs synthétique — le test ne doit contenir que du manuel de préférence)

Utilise `sklearn.model_selection.train_test_split` avec `stratify=`.

### 2.6.3 Test set "golden"

Constitue un **golden test set** manuellement :
- 300 à 500 paires
- Écrites par des experts natifs
- Couvre tous les cas d'usage réels visés
- **Ne quitte JAMAIS ta machine locale ou un stockage chiffré**
- Utilisé pour évaluer chaque version du modèle

C'est la version haïtienne d'un "hold-out set" — c'est ce qui te dira si ton modèle est vraiment bon.

---

## 2.7 AUGMENTATION DE DONNÉES (SI PERTINENT)

Techniques compatibles créole :
1. **Back-translation** : `ht → en → ht` (via NLLB ou Google Translate) pour paraphraser
2. **Paraphrase intra-langue** : `ht → ht` via prompting LLM avec relecture
3. **Instruction rephrasing** : reformuler l'instruction en gardant l'output
4. **Multi-turn expansion** : transformer une paire simple en dialogue à 2-3 tours

**Attention** : n'augmente jamais le test set. Et marque toute paire augmentée dans `tags: ["augmented"]`.

---

## 2.8 GOUVERNANCE DES DONNÉES

Chaque paire doit tracer :
- **Provenance** : d'où vient-elle ?
- **Licence** : qu'est-ce qu'on a le droit d'en faire ?
- **Consentement** : si extraite d'une personne, a-t-elle consenti ?

Documente tout dans `docs/data-card.md` (format HuggingFace Datacard) :
- Sources et licences par source
- Biais connus
- Populations sous-représentées
- Limitations
- Contact pour signalements

Cf. fichier `10_GOUVERNANCE_ET_LICENCES.md` pour le détail.

---

## 2.9 CHECKLIST PHASE 2 (à valider avant Phase 3)

- [ ] Taxonomie de catégories figée et documentée
- [ ] Schéma JSON strict validé par Pydantic/JSONSchema
- [ ] Script `data_quality.py` fonctionne
- [ ] Argilla (ou équivalent) déployé et utilisé
- [ ] Au moins **1 000 paires** curated dans `data/raw/curated/`
- [ ] Splits train/val/test générés de manière reproductible (seed fixé)
- [ ] Golden test set (300+ paires) créé et sauvegardé séparément
- [ ] Datacard rédigée dans `docs/data-card.md`
- [ ] Toutes les données sous DVC
- [ ] Notebook `01_eda.ipynb` avec exploration complète
- [ ] Aucune PII détectée (script passé sans alerte)
- [ ] Distribution équilibrée par catégorie (aucune < 3%)

---

## 2.10 ERREURS MORTELLES À ÉVITER

1. **Ne pas séparer train/test dès le début** → contamination, résultats gonflés
2. **Utiliser 100% de données synthétiques** → le modèle apprend les tics du LLM générateur
3. **Négliger les proverbes et le registre familier** → modèle "trop scolaire", inutilisable
4. **Écrire tout en créole francisé** → trahit la mission de souveraineté
5. **Ignorer les biais régionaux** (Port-au-Prince vs Cap-Haïtien vs Sud) → modèle mono-dialectal
6. **Copier-coller des sites sans droits** → risque juridique majeur
7. **Oublier de sauvegarder les données brutes** → impossible de reconstruire

---

**➡️ Prochaine étape** : `03_ARCHITECTURE_TECHNIQUE.md`
