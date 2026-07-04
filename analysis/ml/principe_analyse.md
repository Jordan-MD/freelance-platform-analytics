# Analyse de données — TP INF232

Module d'analyse statistique et de classification (supervisée et non supervisée) pour le TP INF232.

## Prérequis

Le fichier `dataset.csv` (généré à partir de la graine du groupe, Phase 1 du projet) doit exister avant de lancer l'analyse. Il doit contenir au minimum les colonnes suivantes :

| Colonne | Type | Description |
|---|---|---|
| `id` | entier | Identifiant de l'individu |
| `score_performance` | numérique | Variable quantitative principale |
| `nombre_mission` | numérique | Variable quantitative secondaire |
| `profil` | catégorielle | Étiquette à prédire (ex. "premium" / "standard") |

## Installation

```bash
pip install pandas numpy scipy scikit-learn matplotlib
```

## Utilisation

1. Placez `dataset.csv` dans le même dossier que les fichiers `.py` (ou modifiez la variable `DATA_PATH` en haut de `main.py` pour pointer vers son emplacement réel).
2. Lancez le pipeline complet :

```bash
python3 main.py
```

3. Résultats produits :
   - Console : rapport d'EDA + interprétation automatique de chaque question.
   - `figures/` : 5 graphiques (histogramme, boxplot, scatter+régression, clusters, matrice de confusion).
   - `results/analysis_results.json` : toutes les statistiques, métriques et interprétations, exportées en JSON.

## Architecture des fichiers

| Fichier | Rôle |
|---|---|
| `loader.py` | Charge le CSV et valide sa structure (colonnes attendues) |
| `eda.py` | Exploration initiale : head, info, describe, valeurs manquantes, doublons |
| `q1_statistics.py` | **Q1** — Stat univariée sur `score_performance` : moyenne, médiane, mode, variance, écart-type, quartiles, détection d'outliers (méthode IQR) |
| `q2_correlation.py` | **Q2** — Corrélation de Pearson entre `nombre_mission` et `score_performance`, régression linéaire, évaluation de la fiabilité d'une estimation |
| `q3_clustering.py` | **Q3** — Classification non supervisée : normalisation → méthode du coude → score de silhouette → KMeans (k=3) |
| `q4_classification.py` | **Q4** — Classification supervisée : split train/test → DecisionTreeClassifier → Accuracy/Precision/Recall/F1 → matrice de confusion |
| `visualization.py` | Toutes les fonctions de graphiques (aucun autre module ne trace directement) |
| `utils.py` | Fonctions transverses : création de dossiers, formatage, export JSON |
| `main.py` | Point d'entrée — orchestre le pipeline complet |

## Notes

- Le clustering (Q3) et la classification (Q4) utilisent tous deux `score_performance` et `nombre_mission` comme variables explicatives, mais **sans jamais utiliser `profil`** pour former les clusters (Q3), afin de rester une démarche non supervisée.
- Le nombre de clusters est fixé à 3 (`FINAL_N_CLUSTERS` dans `q3_clustering.py`), mais les scores du coude et de silhouette pour k=2 à 8 sont tout de même calculés et exportés pour justifier ce choix dans le rapport.
- Si une classe de `profil` est très minoritaire dans le dataset, le split stratifié (`train_test_split(..., stratify=y)` dans `q4_classification.py`) peut échouer — vérifier l'équilibre des classes avant exécution.
