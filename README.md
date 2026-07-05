# Plateforme Freelance — Analyse Statistique

Application Streamlit pour l'analyse des performances de 80 freelances sur une plateforme camerounaise.

## Contexte

Une jeune entreprise camerounaise gère une plateforme web qui met en relation des freelances avec des clients. Pour chaque freelance, la plateforme dispose de :

- **Score de performance** (0–100)
- **Nombre de missions** réalisées
- **Étiquette** : `Premium` ou `Standard`

L'application répond à 4 questions métier pour optimiser l'orientation des profils.

## Lancement

```bash
cd freelance-platform-analytics
pip install -r requirements.txt
streamlit run app.py
```

L'application s'ouvre à `http://localhost:8501`.

## Questions d'analyse

| Question | Page | Méthode |
|----------|------|---------|
| Comment se répartit la performance ? Y a-t-il des cas extrêmes ? | Q1 — Répartition | Univariée, boxplot, IQR, Z-score |
| Existe-t-il un lien entre activité et performance ? | Q2 — Corrélation | Pearson, régression linéaire, p-value |
| Mes données révèlent-elles des groupes naturels ? | Q3 — Groupes naturels | K-Means, silhouette, coude |
| Peut-on automatiser l'orientation dès l'inscription ? | Q4 — Automatisation | k-NN, matrice de confusion, F1-score |

## Résultats clés

| Indicateur | Valeur | Interprétation |
|------------|--------|----------------|
| Moyenne performance | 69.7 | Bonne performance globale |
| Corrélation Pearson | 0.673 | Lien significatif missions ↔ performance (p < 0.001) |
| R² | 0.453 | 45% de la performance expliquée par les missions |
| Clusters K-Means | 2 groupes | Silhouette = 0.43 (qualité correcte) |
| Accuracy k-NN | 71% | Bonne prédiction Premium/Standard |
| k optimal | 6 (cross-validation 5-fold) | Meilleur compromis biais-variance |

## Limites du modèle

- Les 80 freelances sont **générés par une formule** (données synthétiques, pas de vraies activités)
- Le lien missions ↔ performance est **injecté artificiellement**
- Les étiquettes Premium/Standard sont calculées par une **formule**, pas par des commerciaux

**Recommandation** : Collecter les vraies données de la plateforme et ré-entraîner les algorithmes.

## Structure du projet

```
freelance-platform-analytics/
├── dataset/
│   ├── dataset_freelance_groupe.csv    # 80 freelances (id, score, missions, profil)
│   └── dataset_generator.py           # Générateur (graine déterministe)
├── src/
│   ├── q1_univariate.py               # Univariée + Z-score + IQR
│   ├── q2_bivariate.py                # Bivariée + Pearson + régression
│   ├── q3_clustering.py               # K-Means + silhouette + coude
│   ├── q4_classification.py           # k-NN optimisé + F1
│   └── utils.py                       # Fonctions utilitaires (camembert)
├── app.py                             # Application Streamlit
└── requirements.txt                   # Dépendances Python
```

## Technologies

- **Streamlit** — Framework web data science
- **Pandas / NumPy** — Manipulation de données
- **Matplotlib / Seaborn** — Visualisation
- **Scikit-learn** — Machine learning (K-Means, k-NN, cross-validation)
- **SciPy** — Tests statistiques
