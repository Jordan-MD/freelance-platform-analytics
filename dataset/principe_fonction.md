# Principe de fonctionnement du générateur de dataset

**Projet : Analyse de Données - Freelances**  
**Package concerné : `dataset/`**  
**Objectif : générer un jeu de données simple, déterministe et exploitable pour les analyses statistiques et le machine learning.**

---

## 1. Idée générale

Le projet génère automatiquement un dataset de **80 freelances fictifs**.

Chaque freelance possède uniquement les colonnes demandées par le sujet :

- `id`
- `score_performance`
- `nombre_mission`
- `profil`

Le but n'est pas de créer un modèle mathématique compliqué. Le but est de produire un dataset :

- facile à expliquer devant un enseignant ;
- réaliste ;
- reproductible ;
- utilisable pour les statistiques descriptives, la corrélation, le clustering et la classification.

Le principe choisi est volontairement simple :

1. On génère d'abord le nombre de missions.
2. On calcule ensuite le score à partir du nombre de missions.
3. On attribue le profil Premium ou Standard à partir du score.
4. On ajoute quelques erreurs volontaires dans les profils pour éviter une classification parfaite.

---

## 2. Pourquoi le dataset est déterministe ?

Le dataset est généré à partir d'une **graine aléatoire**.

Cette graine est calculée avec le nom du chef de groupe :

```python
NOM_CHEF_GROUPE = "JORDAN BENI MBEZOU DJAMEN"
```

Le fichier `seed.py` transforme ce nom en nombre entier. Pour ce projet, la graine obtenue est :

```text
693169457
```

Cette graine sert à initialiser le générateur aléatoire de NumPy :

```python
rng = np.random.default_rng(graine)
```

Cela signifie que :

- le dataset contient de l'aléatoire ;
- mais cet aléatoire est contrôlé ;
- donc deux exécutions avec le même nom donnent exactement le même dataset.

C'est important pour un TP universitaire : le professeur et les membres du groupe peuvent relancer le code et retrouver les mêmes résultats.

---

## 3. Flux global du programme

```text
Nom du chef de groupe
        |
        v
Calcul de la graine
        |
        v
Création du générateur aléatoire rng
        |
        v
Génération des missions
        |
        v
Calcul du score de performance
        |
        v
Attribution du profil Premium / Standard
        |
        v
Validation du dataset
        |
        v
Export du fichier CSV
```

Le fichier principal `run.py` orchestre toutes ces étapes.

---

## 4. Rôle de chaque fichier

### `config.py`

Ce fichier contient les constantes du projet.

Il ne contient pas de logique compliquée. Il sert simplement à centraliser les paramètres :

- nombre de freelances ;
- moyenne et écart-type des missions ;
- formule du score ;
- seuil Premium ;
- taux d'erreurs dans les labels ;
- seuil minimal de corrélation ;
- chemin du fichier CSV.

Exemples de constantes :

```python
N = 80
MISSIONS_MEAN = 45.0
MISSIONS_STD = 22.0
BASE_SCORE = 36.0
MISSION_INFLUENCE = 0.75
SCORE_NOISE_STD = 15.0
PREMIUM_THRESHOLD = 69.0
LABEL_FLIP_RATE = 0.08
```

L'avantage est que si on veut ajuster le comportement du dataset, on modifie uniquement `config.py`.

### `seed.py`

Ce fichier transforme le nom du chef de groupe en graine numérique.

La graine permet de rendre le dataset reproductible.

Ce fichier n'a pas été modifié.

### `models.py`

Ce fichier définit la structure d'un freelance avec une `dataclass`.

Chaque freelance possède exactement les champs suivants :

```python
id: str
score_performance: float
nombre_mission: int
profil: str
```

Ce fichier n'a pas été modifié.

### `generator.py`

Ce fichier contient la logique principale de génération.

Il suit trois grandes étapes :

1. générer les missions ;
2. calculer les scores ;
3. attribuer les profils.

### `validator.py`

Ce fichier vérifie que le dataset généré respecte les règles minimales de qualité.

Si le dataset ne respecte pas les règles, il est rejeté et le programme génère un autre dataset.

### `exporter.py`

Ce fichier exporte les freelances dans un fichier CSV.

Ce fichier n'a pas été modifié.

### `run.py`

Ce fichier lance tout le processus :

1. calcul de la graine ;
2. génération du dataset ;
3. validation ;
4. affichage d'un résumé ;
5. export CSV.

Ce fichier n'a pas été modifié.

---

## 5. Étape 1 : génération du nombre de missions

Le nombre de missions est généré avec une loi normale :

```text
nombre_mission ~ N(45, 22)
```

Cela veut dire que la majorité des freelances auront un nombre de missions autour de 45, mais certains auront moins de missions et d'autres beaucoup plus.

Ensuite, les valeurs sont bornées :

```python
MISSIONS_MIN = 1
MISSIONS_MAX = 150
```

Pourquoi borner les valeurs ?

Parce qu'une loi normale peut parfois produire des valeurs irréalistes, par exemple :

- un nombre de missions négatif ;
- un nombre de missions beaucoup trop grand.

Le bornage garantit donc que le dataset reste cohérent.

Exemple de logique :

```python
missions = rng.normal(MISSIONS_MEAN, MISSIONS_STD, size=n)
missions = np.round(missions)
missions = np.clip(missions, MISSIONS_MIN, MISSIONS_MAX)
```

---

## 6. Étape 2 : calcul du score de performance

Le score est calculé avec une formule simple :

```text
score = BASE_SCORE + nombre_mission * MISSION_INFLUENCE + bruit
```

Dans la configuration actuelle :

```python
BASE_SCORE = 36.0
MISSION_INFLUENCE = 0.75
SCORE_NOISE_STD = 15.0
```

Interprétation :

- `BASE_SCORE` représente le niveau de départ moyen d'un freelance ;
- `MISSION_INFLUENCE` signifie que plus un freelance a fait de missions, plus son score a tendance à augmenter ;
- `SCORE_NOISE_STD` ajoute du bruit pour rendre les données plus réalistes.

Le bruit est important. Sans bruit, deux freelances avec le même nombre de missions auraient presque toujours le même score, ce qui serait trop artificiel.

Avec le bruit :

- un freelance avec beaucoup de missions peut parfois avoir un score moyen ;
- un freelance avec moins de missions peut parfois avoir un bon score ;
- la relation reste positive, mais pas parfaite.

Après le calcul, le score est borné entre 0 et 100 :

```python
score = np.clip(score, 0, 100)
```

Cela respecte la logique d'un score de performance exprimé sur 100.

---

## 7. Étape 3 : attribution du profil Premium ou Standard

Le profil est calculé à partir d'un indice Premium.

Dans notre cas, l'indice est basé sur le score :

```text
indice_premium = score + bruit
```

Puis on applique une règle très simple :

```text
si indice_premium >= PREMIUM_THRESHOLD
    profil = "Premium"
sinon
    profil = "Standard"
```

Dans la configuration actuelle :

```python
PREMIUM_THRESHOLD = 69.0
PREMIUM_NOISE_STD = 0.5
```

Explication :

- un score élevé augmente les chances d'être Premium ;
- un score faible augmente les chances d'être Standard ;
- un petit bruit permet d'éviter une frontière trop rigide.

Cette logique est facile à justifier : dans la réalité, un profil Premium dépend souvent d'une bonne performance, mais il peut y avoir une petite part d'incertitude.

---

## 8. Étape 4 : ajout volontaire d'erreurs de classification

Après l'attribution des profils, le programme inverse environ 8 % des labels.

Dans la configuration actuelle :

```python
LABEL_FLIP_RATE = 0.08
```

Comme le dataset contient 80 freelances :

```text
80 * 0.08 = 6.4
```

Le programme inverse donc environ 6 labels.

Exemple :

- certains `Premium` deviennent `Standard` ;
- certains `Standard` deviennent `Premium`.

Pourquoi faire cela ?

Parce qu'un dataset trop parfait donnerait une classification à 100 %, ce qui serait peu réaliste.

Dans un vrai contexte, les données peuvent contenir :

- des erreurs humaines ;
- des décisions subjectives ;
- des cas limites ;
- des profils atypiques.

Ces erreurs volontaires rendent la classification plus intéressante : le modèle doit apprendre une tendance générale, mais il ne peut pas tout prédire parfaitement.

---

## 9. Pourquoi la corrélation missions / score est positive ?

La corrélation est positive parce que le score dépend en partie du nombre de missions :

```text
score = BASE_SCORE + nombre_mission * MISSION_INFLUENCE + bruit
```

Comme `MISSION_INFLUENCE = 0.75`, chaque mission supplémentaire augmente en moyenne le score.

Mais la corrélation n'est pas égale à 1, car il y a du bruit.

C'est exactement ce qu'on veut :

- une relation claire entre missions et score ;
- mais pas une relation parfaite ;
- donc des données plus réalistes.

Avec la configuration actuelle, la corrélation obtenue est :

```text
0.673
```

Elle est donc comprise entre 0.60 et 0.80, ce qui correspond à l'objectif du TP.

---

## 10. Pourquoi le clustering peut retrouver 3 groupes ?

Même si le programme ne crée pas directement trois profils cachés, les données forment naturellement des zones.

Comme les missions influencent le score, on observe généralement :

- des freelances avec peu de missions et un score plus faible ;
- des freelances intermédiaires ;
- des freelances avec beaucoup de missions et un score plus élevé.

Avec KMeans en 3 groupes, les centres obtenus sont environ :

| Groupe | Score moyen | Missions moyennes | Interprétation simple |
| ------ | ----------- | ----------------- | --------------------- |
| 1      | 39.2        | 23.0              | freelances moins performants / moins expérimentés |
| 2      | 68.5        | 41.5              | freelances intermédiaires |
| 3      | 86.5        | 62.6              | freelances plus performants / plus expérimentés |

Cela donne une interprétation simple et naturelle pour la partie clustering.

---

## 11. Pourquoi la classification n'est pas parfaite ?

La classification cherche à prédire `profil` à partir de :

- `score_performance`
- `nombre_mission`

Le profil dépend principalement du score, donc un modèle peut apprendre une bonne règle de séparation.

Mais la précision n'est pas de 100 %, car :

- un petit bruit est ajouté dans l'indice Premium ;
- environ 8 % des labels sont inversés volontairement ;
- certains freelances sont proches du seuil Premium.

Avec une validation croisée simple, les résultats observés sont autour de :

```text
DecisionTreeClassifier(max_depth=2) : accuracy moyenne ≈ 0.900
RandomForestClassifier(max_depth=3) : accuracy moyenne ≈ 0.887
KNeighborsClassifier(n_neighbors=5) : accuracy moyenne ≈ 0.887
```

Ces valeurs sont dans la zone souhaitée : environ 88 % à 94 %, sans obtenir 100 %.

---

## 12. Validation du dataset

Le fichier `validator.py` vérifie plusieurs règles :

- aucun score hors de l'intervalle `[0, 100]` ;
- aucun nombre de missions négatif ;
- présence des deux classes `Premium` et `Standard` ;
- corrélation missions / score supérieure ou égale à `MIN_CORRELATION` ;
- nombre attendu de freelances ;
- unicité des identifiants.

Dans la configuration actuelle :

```python
MIN_CORRELATION = 0.60
```

Si une règle n'est pas respectée, le dataset est rejeté et une nouvelle tentative est lancée.

Avec la configuration actuelle, le dataset est validé dès la première tentative.

---

## 13. Résultats actuels du dataset

Après exécution de :

```bash
python dataset/run.py
```

ou, selon l'environnement :

```bash
.venv/bin/python dataset/run.py
```

On obtient :

```text
Graine obtenue : 693169457
Dataset valide obtenu en 1 tentative
Nombre de freelances générés : 80
Corrélation missions/score : 0.673
Répartition : 43 Premium / 37 Standard
```

Autres statistiques utiles :

```text
Score moyen : 69.679
Nombre moyen de missions : 45.662
Score minimum / maximum : 26.6 / 100.0
Missions minimum / maximum : 1 / 82
```

On observe aussi quelques valeurs atypiques :

```text
Scores très faibles ou très élevés : 10
Missions très faibles ou élevées : 3
```

Ces valeurs atypiques sont utiles pour rendre l'analyse plus intéressante.

---

## 14. Ce que le projet n'utilise pas

Pour rester simple et pédagogique, le générateur n'utilise pas :

- matrice de covariance ;
- `multivariate_normal()` ;
- régression logistique ;
- logit ;
- sigmoid ;
- normalisation des variables.

Le choix est volontaire : le dataset doit pouvoir être expliqué facilement par tous les membres du groupe.

La logique principale peut se résumer en une phrase :

> Plus un freelance a de missions, plus son score a tendance à être élevé ; plus son score est élevé, plus il a de chances d'être Premium, avec un peu de bruit et quelques erreurs volontaires pour rester réaliste.

---

## 15. Résumé final

Le générateur produit un dataset :

- déterministe grâce à la graine calculée avec le nom du chef de groupe ;
- simple à comprendre ;
- limité aux colonnes demandées ;
- cohérent statistiquement ;
- exploitable pour la corrélation ;
- exploitable pour le clustering ;
- exploitable pour la classification ;
- non parfait, donc plus réaliste.

Ce principe correspond bien à l'objectif du TP : construire un jeu de données clair, justifiable et adapté à une analyse de données complète.
