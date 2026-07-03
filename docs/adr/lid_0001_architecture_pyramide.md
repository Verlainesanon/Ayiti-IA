# ADR 0001 : Architecture "Pyramide de la Robustesse" pour le LID

* **Statut** : Accepté
* **Auteurs** : Assistant Ayiti-AI & Équipe technique
* **Date** : 2026-07-03

## Contexte et Problématique

Ayiti-AI doit être équipé d'un système de Détection de Langue (Language Identification - LID) ultra-robuste en production, capable d'identifier le créole haïtien (`ht`), le français (`fr`) et l'anglais (`en`). 

L'approche naïve initialement envisagée (utilisation de DistilBERT combiné à une simple wordlist statique) présente des limitations majeures :
1. **Empreinte mémoire excessive** : ~500 Mo de RAM, ce qui s'oppose à la contrainte matérielle de déploiement (Dell CPU local, < 50 Mo de RAM).
2. **Latence trop élevée** : 200-300 ms sur CPU, ce qui fait du guardrail un goulot d'étranglement.
3. **Absence de gestion du code-switching** : Le créole haïtien écrit comporte un taux important d'alternance codique (code-switching) avec le français et l'anglais. Un classifieur binaire naïf échoue dans 40% des cas mixtes.
4. **Pas d'explicabilité** : Incapacité d'expliquer pourquoi une phrase a été détectée dans telle langue.

## Décision

Nous adoptons une architecture en cascade dite **"Pyramide de la Robustesse"** à 3 niveaux :

```
                        ▲
                       / \
                      /   \     Niveau 3 : CharCNN custom (3-5 ms) - Cas ambigus / noisés
                     /     \
                    /───────\   Niveau 2 : FastText lid.176.bin (1-2 ms) - Modèle statistique
                   /         \
                  /───────────\ Niveau 1 : Règles déterministes (<0.5 ms) - Marqueurs exclusifs
                 /             \
                └───────────────┘
```

1. **Niveau 1 : Règles déterministes** (< 0.5 ms)
   * Utilise une liste de marqueurs linguistiques exclusifs validés (ex: particules TMA créoles comme `ap`, `pral`, `fèk`).
   * Détecte les combinaisons exclusives de diacritiques (comme la lettre `ò` en créole, ou les ligatures `œ` en français).
   * Si un signal fort est trouvé, la décision est prise immédiatement avec une confiance de 1.0 (Early Exit).

2. **Niveau 2 : FastText (`lid.176.bin`)** (1-2 ms)
   * Modèle statistique compressé de Facebook AI (~2 Mo) pré-entraîné sur 176 langues.
   * Si la prédiction a un score >= 0.80, la décision est retournée directement.

3. **Niveau 3 : CharCNN Custom** (3-5 ms)
   * Petit modèle de réseau de neurones convolutif au niveau des caractères, entraîné localement sur Dell CPU (en moins de 10 min) sur les corpus spécifiques d'Ayiti-AI.
   * Gère les fautes d'orthographe, le texte bruité, et les phrases très courtes non détectées par les niveaux 1 & 2.

### Décision sur la stratégie de Code-Switching

Nous choisissons la **Stratégie B (Multi-labels)** en interne :
* L'API renvoie un dictionnaire complet des scores détectés (ex: `{"ht": 0.65, "fr": 0.35}`).
* Si une langue secondaire dépasse un seuil de `0.30` (configurable), le drapeau `is_code_switched` est activé.
* Pour la compatibilité avec les clients requérant une classification binaire, nous exposons un champ `primary_language` représentant la langue matricielle (celle qui régit la syntaxe grammaticale, souvent identifiée par ses particules TMA).

## Conséquences

* **Performance** : Latence moyenne réduite de 200ms à moins de 5ms. Empreinte mémoire réduite de 500Mo à moins de 10Mo.
* **Robustesse** : Défense en profondeur. Si le modèle de caractères ou FastText est indisponible ou échoue, les règles déterministes prennent le relais et vice-versa.
* **Maintenabilité** : Les marqueurs du Niveau 1 sont externalisés dans un fichier YAML (`config/lid_markers.yaml`) et peuvent être mis à jour sans modification de code.
* **Explicabilité** : Les marqueurs de langue détectés par le Niveau 1 sont retournés dans les métadonnées de l'output, permettant de tracer précisément la décision.
* **Souveraineté** : Aucun appel réseau externe n'est requis au runtime.
