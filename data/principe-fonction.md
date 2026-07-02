# Bilan — Génération du jeu de données (Thème B : Plateforme Freelance)

**Statut : ✅ TERMINÉ — prêt à être utilisé par Data Science et Dev**

---

## 🟢 PARTIE 1 — Résumé accessible (pour tout le monde)

### Ce qu'on a fait

On a créé un jeu de données de **80 freelances fictifs**, généré automatiquement à partir du nom du chef de groupe (Jordan), de façon à ce que :

- **Personne d'autre au monde n'aura exactement les mêmes données** (chaque nom produit un résultat différent)
- **Si on relance le script, on obtient toujours EXACTEMENT le même résultat** (c'est ce qu'on appelle "déterministe" — obligatoire selon l'énoncé du prof)

### Ce que chaque freelance a comme informations

| Donnée                           | Exemple                            | À quoi ça sert                                   |
| -------------------------------- | ---------------------------------- | ------------------------------------------------ |
| Domaine                          | Développeur / Designer / Rédacteur | Affichage seulement                              |
| Années d'expérience              | 6.6 ans                            | Affichage seulement                              |
| **Nombre de missions réalisées** | 44                                 | **Utilisé pour les calculs statistiques**        |
| **Score de performance (0-100)** | 70.6                               | **Utilisé pour les calculs statistiques**        |
| Tarif horaire                    | 5150 FCFA                          | Affichage seulement                              |
| Temps de livraison moyen         | 5.9 jours                          | Affichage seulement                              |
| Taux de réponse                  | 53.5%                              | Affichage seulement                              |
| **Statut Premium/Standard**      | Premium                            | **C'est ce qu'on doit apprendre à prédire (Q4)** |

Seules **2 variables** (nombre de missions + score de performance) et l'étiquette Premium/Standard rentrent dans les calculs notés. Le reste (domaine, tarif, expérience...) sert juste à rendre la plateforme réaliste visuellement.

### Pourquoi les données ne sont pas "trop parfaites"

On a volontairement mis du réalisme imparfait dans les données :

- Le lien entre "nombre de missions" et "score" existe et est fort, mais **pas parfait** (il y a des exceptions)
- L'étiquette Premium/Standard contient volontairement **8% d'erreurs** — pour simuler le fait que dans la vraie vie, l'équipe commerciale se trompe parfois en classant les gens "au feeling"

**Pourquoi c'est important** : si les données étaient parfaites, la Q4 (prédiction automatique) donnerait 100% de réussite, ce qui n'aurait aucun intérêt à discuter à l'oral. Là, on a une vraie marge d'erreur (~80% de bonnes prédictions) qu'on peut analyser et commenter.

### Chiffres clés à retenir pour l'oral

- **Graine (seed) : 471970376**, obtenue à partir de `JORDANBENIMBEZOUDJAMEN`
- **80 freelances** générés
- **Corrélation missions↔score : 0.83** (forte relation positive)
- **3 profils cachés** dans les données (débutants / réguliers / vétérans) que le clustering (Q3) devra retrouver
- **~80% d'exactitude** attendue pour la prédiction Premium/Standard (Q4)

---

## 🔧 PARTIE 2 — Détails techniques (pour Data Science & Dev)

Fichier : `data/generate_data.py`. Organisé en fonctions pures indépendantes (aucun effet de bord), donc importable et testable.

### `name_to_seed(nom_complet) -> int`

Transforme le nom du chef de groupe en un nombre entier unique via un hash polynomial (base 31). Déterministe : même nom → toujours la même graine. C'est cette graine qui pilote tout le reste du hasard généré.

### `generate_profile_assignments(rng, n, profils) -> array`

Tire au hasard, pour chacun des 80 freelances, un profil caché parmi les 3 définis (débutant 40%, régulier 35%, vétéran 25%). Ce tirage n'apparaît dans aucune colonne du dataset final — c'est la "vérité cachée" que la Q3 (clustering) doit retrouver sans la connaître.

### `generate_ml_variables(rng, profile_assignments, profils, correlation) -> (missions, score)`

Pour chaque profil, génère les valeurs de `nombre_missions` et `score_performance` via une distribution statistique à deux dimensions corrélées (loi normale bivariée). C'est cette fonction qui crée la corrélation de 0.83 entre les deux variables.

### `generate_labels(rng, missions, score, flip_rate) -> array`

Calcule l'étiquette Premium/Standard à partir d'une formule qui combine le score et le nombre de missions (avec un poids un peu plus fort sur le score), puis **inverse volontairement 8% des étiquettes** pour simuler les erreurs humaines de classement.

### `generate_display_variables(rng, missions, score, ...) -> dict`

Génère les colonnes non utilisées dans les calculs (domaine, expérience, tarif, délai, taux de réponse), en les reliant logiquement aux vraies variables pour que ça reste cohérent visuellement (ex : meilleur score → livraison plus rapide).

### `build_dataset(nom_chef_groupe, n, profils) -> (dataframe, seed, profile_assignments)`

**La fonction à utiliser si vous voulez régénérer les données depuis un autre script** (notebook d'analyse, backend FastAPI...). Elle enchaîne toutes les étapes ci-dessus et retourne un DataFrame pandas prêt à l'emploi. N'écrit rien sur le disque, n'affiche rien — 100% réutilisable.

### `compute_diagnostics(df, profile_assignments) -> dict`

Calcule les indicateurs de vérification (corrélation, répartition des labels, répartition des profils) sous forme de dictionnaire, pour que Data Science puisse les réutiliser dans son propre code sans dupliquer les calculs.

### `main()`

Le seul endroit du fichier qui affiche des choses dans la console et écrit le fichier CSV. C'est ce qui s'exécute quand on lance `python generate_data.py` directement.

---

## ➡️ PARTIE 3 — Comment chaque pôle doit utiliser ça

**Data Science** : partez directement du fichier `dataset_freelance_groupe.csv` (ou appelez `build_dataset()` si vous voulez tester avec un `n` plus grand pour vérifier la robustesse de vos méthodes). Les 2 colonnes qui vous intéressent pour les calculs sont `nombre_missions`, `score_performance`, et la cible `profil_type`.

**Dev (Backend)** : vous pouvez soit lire le CSV directement (`data_loader.py`), soit importer `build_dataset()` si vous voulez régénérer à la demande depuis l'API `/api/generate`.

**Documentation** : les chiffres clés de la Partie 1 (graine, N=80, corrélation 0.83, 3 profils, ~80% accuracy attendue) sont ce qu'il faut mettre dans la section "Annexe — génération des données personnalisées" du rapport.

**Tout le monde, en vue de l'oral** : si le prof vous interroge sur la génération, vous devez pouvoir expliquer en une phrase : _"on a transformé le nom du chef de groupe en un nombre (la graine), qui a servi à générer aléatoirement mais de façon reproductible 80 freelances répartis en 3 profils cachés, avec une corrélation réaliste entre leurs missions et leur score, et une étiquette Premium/Standard volontairement imparfaite pour rester réaliste."_
