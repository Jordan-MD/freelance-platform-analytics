# Dataset Generator

Ce fichier `dataset_generator.py` regroupe l'ensemble de la génération du dataset en un seul script.

Il inclut :
- la configuration du jeu de données,
- la génération des missions, des scores et des niveaux Premium/Standard,
- la validation des règles métiers (corrélation minimale, identifiants uniques, répartition Premium/Standard, etc.),
- l'export du dataset final en CSV.

## Exécution

Depuis le dossier `freelance-platform-analytics`, lancez :

```powershell
python .\dataset\dataset_generator.py
```

Le fichier produit sera écrit dans `freelance-platform-analytics/dataset/dataset_freelance_groupe.csv`.
