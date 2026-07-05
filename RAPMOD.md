# Rapport des modifications

## Date : 5 juillet 2026

---

## 1. q2_bivariate.py — Formule erreur type

**Avant :**
```python
erreur_type = (y - modele.predict(X)).std()
```

**Après :**
```python
erreur_type = np.sqrt(np.sum((y - modele.predict(X))**2) / (len(y) - 2))
```

**Pourquoi :** La formule `.std()` utilise `n-1` (échantillon), mais l'erreur type de la régression utilise `n-2` (degrés de liberté).

**Résultat :** 13.82 (au lieu de ~13.73)

---

## 2. q1_univariate.py — Ajout du Z-score

**Ajout :** Calcul du Z-score par freelance et détection des outliers avec |Z| > 3.

```python
z_scores = (score - moyenne) / ecart_type
outliers_zscore = df[abs(z_scores) > 3]
```

**Résultat :** 80 z-scores calculés, 0 outlier avec |Z| > 3

---

## 3. q4_classification.py — Optimisation k-NN

**Modifications :**
- `fillna(0)` → `fillna(median)` (plus robuste aux valeurs extrêmes)
- k optimisé par cross-validation 5-fold (plage 1-15) au lieu de k=3
- Ajout de la précision, du rappel et du F1-score via `classification_report`
- Suppression du diagnostic inutile (min==0 && var==0)
- Suppression de l'import pandas non utilisé

**Résultat :** k=13 (au lieu de 3), accuracy=79.2%, F1=78.2%

---

## 4. app.py — Interface

**Modifications :**
- "90%" → "71%" (accuracy réelle)
- Ajout section "Limites du modèle" (données synthétiques)
- Ajout affichage Z-score dans Q1 (expander + tableau)
- Ajout graphique optimisation de k dans Q4
- 5 KPIs dans Q4 (accuracy, précision, rappel, F1, k optimal) au lieu de 3
- Détails techniques k-NN mis à jour

---

## 5. q3_clustering.py — Nettoyage

- Suppression de `silhouette_samples` (non utilisé)
- Import `silhouette_score` conservé

---

## 6. Imports inutilisés

- `pandas` supprimé de `q2_bivariate.py`
- `pandas` supprimé de `q4_classification.py`

---

## Résumé des résultats

| Indicateur | Avant | Après |
|------------|-------|-------|
| erreur_type Q2 | 13.73 (.std()) | 13.82 (sqrt(SSE/n-2)) |
| k-NN k | 3 (fixe) | 13 (CV 5-fold) |
| Accuracy Q4 | ~71% | 79.2% |
| F1-score Q4 | — | 78.2% |
| Outliers Z>3 | — | 0 |
| "fiabilité" Accueil | 90% | 71% |
