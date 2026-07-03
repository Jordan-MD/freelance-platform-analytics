# Principe de fonctionnement — Générateur de dataset (Thème B : Freelance)

**Package : `dataset/`**
**Statut : ✅ Fonctionnel et validé**

---

## 🟢 Vue d'ensemble (accessible à tous)

Ce module génère automatiquement un jeu de **80 freelances fictifs**, de façon :

- **Unique** au groupe : basé sur le nom du chef de groupe, personne d'autre n'aura les mêmes données
- **Reproductible** : relancer le programme redonne toujours exactement le même résultat
- **Auto-vérifié** : si jamais les données générées ne respectent pas certaines règles de cohérence (score hors limites, aucune corrélation, etc.), le programme les rejette et regénère tout seul, sans intervention humaine

### Schéma du flux de génération

```
┌──────────────────────────────┐
│ 1. Nom du chef de groupe     │
│    "JORDAN BENI MBEZOU..."   │
└──────────────┬───────────────┘
               │  seed.py
               ▼
┌─────────────────────────────┐
│ 2. Graine numérique         │
│    1855035594               │
└──────────────┬──────────────┘
               │  crée le générateur aléatoire (rng)
               ▼
┌──────────────────────────────┐
│ 3. Génération des freelances │◄────┐  generator.py
│    (score, missions, profil) │     │
└──────────────┬───────────────┘     │
               ▼                     │
┌──────────────────────────────┐     │  Si invalide :
│ 4. Validation                │─────┘  on régénère avec
│    (validator.py)            │        le MÊME rng
└──────────────┬───────────────┘
               │  Si valide ✅
               ▼
┌───────────────────────────────┐
│ 5. Export CSV                 │  exporter.py
│    dataset_freelance_groupe   │
└───────────────────────────────┘
```

### Chiffres actuels (config par défaut)

- Graine obtenue : **693169457**
- Taille de l'échantillon : **80 freelances**
- Corrélation missions ↔ score : **0.722**
- Répartition : **45 Premium / 35 Standard**
- Validé dès la **1ère tentative**

### Pourquoi une boucle de validation, si tout marche déjà ?

Parce que la génération reste basée sur du tirage aléatoire (même s'il est reproductible) : sur un petit échantillon, il existe une faible probabilité qu'un tirage donne, par exemple, une corrélation négative par pur hasard statistique, ou qu'aucun freelance ne soit classé "Standard". Plutôt que de livrer un dataset boiteux sans s'en rendre compte, le programme vérifie lui-même et recommence si besoin — c'est un filet de sécurité, pas une étape qui doit normalement se déclencher souvent.

---

## 🔧 Détails techniques (par module)

### `seed.py` — `generer_graine_groupe(nom_complet) -> int`

Transforme le nom du chef de groupe en un entier :

1. Normalise les caractères Unicode et retire les accents (`unicodedata`) — robuste même si un nom contient des accents.
2. Passe en majuscules, retire les espaces.
3. Hash polynomial (base `p=31`) sur le code ASCII de chaque caractère, modulo `m=2**31-1`.

Déterministe (même nom → même graine) et sensible à l'ordre des lettres (deux noms anagrammes donnent des graines différentes).

### `config.py` — constantes globales

Centralise tous les paramètres ajustables : nom du chef de groupe, taille d'échantillon (`N`), moyennes/écarts-types des variables, poids de la règle de classification, taux de bruit sur les étiquettes, nombre max de tentatives de régénération, chemin d'export. **Aucune logique exécutable** — uniquement des valeurs, pour que tout ajustement de paramètre se fasse à un seul endroit.

### `models.py` — `Freelance` (dataclass)

Structure représentant un freelance généré, avec 4 champs :

- `id: str` — identifiant (ex: `FR001`)
- `score_performance: float` — variable ML n°1
- `nombre_mission: int` — variable ML n°2
- `profil: str` — `"Premium"` ou `"Standard"` (cible à prédire en Q4)

`frozen=True` : une fois créé, l'objet ne peut plus être modifié par erreur ailleurs dans le code.

### `generator.py` — logique de génération

- `generate_ml_variables(...)` : tire `nombre_mission` et `score_performance` via une **loi normale bivariée corrélée** (une seule population pour l'instant, sans sous-groupes cachés), puis borne les valeurs dans des plages réalistes.
- `generate_labels(...)` : calcule `profil` via une règle logistique (combinaison pondérée de `score` et `missions`, passée dans une sigmoïde) puis **inverse volontairement ~8% des étiquettes**, pour simuler un classement humain imparfait plutôt qu'une règle parfaite.
- `generate_freelances(rng, n)` : assemble tout et retourne la liste de `Freelance`.

Aucune fonction de ce module n'affiche ni n'écrit de fichier — uniquement du calcul, donc réutilisable et testable isolément.

### `validator.py` — validation + régénération

- `valider(freelances)` retourne `(est_valide, liste_erreurs)` en vérifiant :
  - ✅ aucune valeur négative (`nombre_mission`)
  - ✅ `score_performance` entre 0 et 100
  - ✅ aucun champ vide
  - ✅ au moins un `Premium` présent
  - ✅ au moins un `Standard` présent
  - ✅ corrélation missions/score strictement positive
- `generer_dataset_valide(rng, n, max_attempts)` boucle : génère, valide, et **si invalide, régénère en continuant de tirer depuis le même `rng`** (jamais recréé à partir d'une nouvelle graine). Retourne le dataset validé + le nombre de tentatives effectuées.

**Point clé sur le déterminisme :** comme le `rng` découle uniquement de la graine initiale, toute la séquence de tentatives est elle-même déterministe. Pour un même nom, le nombre de tentatives nécessaires et le dataset final accepté seront **toujours identiques** d'une exécution à l'autre — testé et confirmé (voir section suivante).

### `exporter.py` — `export_csv(freelances, path)`

Écrit la liste de `Freelance` dans un fichier CSV, avec les colonnes dans l'ordre des champs de la dataclass.

### `run.py` (racine du repo) — point d'entrée

Orchestre l'ensemble : génère la graine, crée le `rng`, appelle `generer_dataset_valide`, affiche un résumé (graine, tentatives, corrélation, répartition Premium/Standard), exporte le CSV.

---

## ✅ Tests effectués

| Test                                                                       | Résultat                                                                                                                                                             |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exécution normale (config par défaut)                                      | Validé en 1 tentative, corrélation 0.722, 45 Premium / 35 Standard                                                                                                   |
| Déterminisme (2 exécutions successives)                                    | CSV strictement identique (`diff` = aucune différence)                                                                                                               |
| Stress-test (paramètres volontairement instables : corrélation forcée à 0) | Échec détecté et affiché ("corrélation non positive"), régénération automatique réussie à la tentative 2, **résultat strictement identique sur 2 runs indépendants** |

---

## ⚠️ Limite actuelle à connaître

La génération repose sur **une seule population** (pas de sous-groupes/profils latents cachés). Ça garantit une bonne corrélation pour Q2, mais si Q3 (clustering) ne trouve pas de groupes naturels convaincants sur ces données, il faudra réintroduire une structure en plusieurs profils (ex: débutant/intermédiaire/expert) à ce moment-là — actuellement décidé comme non prioritaire, à traiter quand Data Science attaquera cette question.
