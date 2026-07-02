# 🇭🇹 Ayiti-AI — Tableau de Bord des Tâches et Objectifs

Ce document répertorie l'état d'avancement des fonctionnalités de la plateforme de fine-tuning d'**Ayiti-AI**. Il est mis à jour à chaque étape franchie.

---

## 📊 Résumé du Projet

* **Objectif** : Créer un pipeline complet et robuste pour le fine-tuning et l'évaluation d'un modèle souverain haïtien (**Qwen2.5**) en Kreyòl ayisyen (`ht`), Français (`fr`) et Anglais (`en`).
* **Statut Actuel** : Inférence, évaluation et tests unitaires terminés. Correction finale de la boucle d'entraînement en cours.

---

## 🛠️ État des Tâches

### 1. 🐛 Correctifs de Bugs Critiques (Base du Pipeline)
- [x] **Unifier les signatures de chargement de modèle**
  - *Détail* : Harmoniser `qwen_loader.py` avec `trainer.py` via `load_qwen_model_and_tokenizer()`.
- [x] **Ajouter la configuration LoRA dynamique**
  - *Détail* : Ajouter `get_lora_config()` dans `lora_adapter.py` pour PEFT.
- [x] **Mettre à jour les exports globaux**
  - *Détail* : Nettoyer `src/models/__init__.py`.

### 2. 🗂️ Gestion et Collecte de Données (Kreyòl Seed)
- [x] **Créer un jeu de données de test (Seed Dataset)**
  - *Détail* : Établir `data/raw/seed_ht.jsonl` avec 21 invites représentatives (histoire, culture, grammaire).
- [x] **Créer le script de collecte et validation de données**
  - *Détail* : Développer `scripts/collect_data.py` pour valider le JSONL, fusionner et convertir CSV.
- [x] **Résoudre les problèmes d'encodage Windows (UnicodeEncodeError)**
  - *Détail* : Forcer l'encodage `utf-8` sur stdout/stderr pour l'affichage correct des emojis.

### 3. 💬 Interface d'Inférence et Chat
- [x] **Développer la classe de chat interactive multilingue**
  - *Détail* : Créer `src/inference/chat.py` capable de charger les modèles de base ou avec adaptateurs LoRA.
- [x] **Ajouter les prompts système personnalisés par langue**
  - *Détail* : Intégrer les prompts d'identité "Ayiti-AI" en `ht`, `fr`, `en`.

### 4. 📈 Suite d'Évaluation (Metrics)
- [x] **Implémenter le calcul de BLEU**
  - *Détail* : Ajouter `compute_bleu()` via `sacrebleu`.
- [x] **Implémenter le calcul de ROUGE**
  - *Détail* : Ajouter `compute_rouge()` pour ROUGE-1, ROUGE-2, ROUGE-L.
- [x] **Implémenter le calcul de la Perplexité**
  - *Détail* : Ajouter `compute_perplexity()` pour évaluer la fluidité du modèle.
- [x] **Créer la fonction d'évaluation globale**
  - *Détail* : Intégrer les prédictions et scores automatisés dans `src/evaluation/metrics.py`.

### 5. 🧪 Tests Unitaires et Qualité du Code
- [x] **Valider le projet par les tests pytest**
  - *Détail* : Lancement des suites de tests pour `dataset_builder` et `lora_config`. (Terminé : 31/31 tests réussis)
- [x] **Ajouter les configurations de commande (Makefile, requirements.txt)**
  - *Détail* : Mettre à jour le `Makefile` pour simplifier les commandes CLI (`make test`, `make train`, `make inference`).

### 6. 🏋️ Entraînement SFT (Fine-Tuning)
- [x] **Corriger le formateur de batch dans `trainer.py`**
  - *Détail* : Ajuster `formatting_prompts_func` pour prendre en compte les colonnes `instruction`/`output` dynamiquement au lieu de chercher une clé `messages` inexistante.
- [/] **Lancer un entraînement de test (CPU/Local)**
  - *Détail* : Valider le fonctionnement complet du pipeline avec `make train`. (En cours)

---

## 🚀 Prochaines Étapes Immédiates
1. Lancer l'entraînement SFT de validation locale (CPU) sur le seed dataset.
2. Évaluer et valider l'adaptateur LoRA généré.

