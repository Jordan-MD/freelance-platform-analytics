# Plateforme Freelance — Analyse Statistique (Streamlit)

## Structure du projet

```
my_project/
├── dataset/
│   └── dataset_freelance_groupe.csv    # Dataset généré
│   └── dataset_generator.csv           # Générateur dataset
├── src/
│   ├── __init__.py
│   ├── utils.py                        # Fonctions utilitaires (camembert)
│   ├── q1_univariate.py                # Q1 : Statistique univariée + IQR
│   ├── q2_bivariate.py                 # Q2 : Corrélation Pearson + Régression
│   ├── q3_clustering.py                # Q3 : Clustering K-Means non supervisé
│   └── q4_classification.py            # Q4 : Classification k-NN supervisée
├── app.py                              # Point d'entrée Streamlit
├── requirements.txt                    # Dépendances Python
└── README.md                           # Ce fichier
```

## Installation

```bash
cd my_project
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans le navigateur à `http://localhost:8501`.

## Navigation

| Page                      | Contenu                                                                |
| ------------------------- | ---------------------------------------------------------------------- |
| **Accueil**               | Vue d'ensemble, KPIs, aperçu du dataset, téléchargement CSV            |
| **Q1 — Répartition**      | Distribution des scores, boxplot, détection des outliers (IQR)         |
| **Q2 — Corrélation**      | Nuage de points, régression linéaire, simulateur d'anticipation        |
| **Q3 — Groupes naturels** | Méthode du coude, silhouette, clusters K-Means, fiches profil          |
| **Q4 — Automatisation**   | Matrice de confusion k-NN, simulateur de prédiction, risque commercial |

## Architecture des modules

| Fichier                | Méthode exposée                                    | Retour                                                      |
| ---------------------- | -------------------------------------------------- | ----------------------------------------------------------- |
| `q1_univariate.py`     | `analyser_performance_q1(df)`                      | `(metriques, fig_box, fig_hist, interpretation)`            |
| `q2_bivariate.py`      | `analyser_relations_q2(df)`                        | `(metriques, fig_scatter, scenarios)`                       |
| `q3_clustering.py`     | `analyser_profils_q3(df, features)`                | `(metriques, fig_selection, fig_clusters, interpretation)`  |
| `q4_classification.py` | `analyser_classification_q4(df, features, target)` | `(model, scaler, metriques, fig_confusion, interpretation)` |
