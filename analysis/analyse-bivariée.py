import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression

# 1. CHARGEMENT DES DONNÉES
# Le script est dans analysis/ml/, le CSV est dans data/ à la racine du projet
# => on remonte de deux niveaux avant de redescendre dans data/
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "..", "data", "dataset_freelance_groupe.csv")
csv_path = os.path.normpath(csv_path)

try:
    df = pd.read_csv(csv_path)
    print("Jeu de données chargé avec succès !")
    print(f"Nombre de freelances à analyser : {len(df)}\n")
except FileNotFoundError:
    print(f"Erreur : fichier introuvable à l'emplacement : {csv_path}")
    print("Vérifie l'arborescence de ton dossier data/ par rapport à ce script.")
    exit()

# Définition des variables clés
X_var = "nombre_missions"
Y_var = "score_performance"

# 2. CORRÉLATION DE PEARSON + TEST DE SIGNIFICATIVITÉ
# Le coefficient seul ne suffit pas : sur un échantillon de 80 personnes, la
# fondatrice demande "est-ce vrai dans mes données ?" -> il faut vérifier que
# ce lien n'est pas dû au hasard (p-value), pas seulement en donner la force.
correlation, p_value = pearsonr(df[X_var], df[Y_var])

print("--- ANALYSE DE CORRÉLATION ---")
print(f"Coefficient de corrélation de Pearson : {correlation:.3f}")
print(f"p-value du test de significativité      : {p_value:.2e}")

if p_value < 0.05:
    print("=> Le lien est statistiquement significatif (p < 0.05) : il est très")
    print("   improbable qu'il soit dû au hasard sur cet échantillon.")
else:
    print("=> Le lien n'est PAS statistiquement significatif (p >= 0.05) : au vu")
    print("   de la taille de l'échantillon, on ne peut pas affirmer qu'il existe")
    print("   réellement dans la population de freelances.")

if correlation > 0.7:
    print("Force du lien : TRÈS FORTE et positive. Plus le nombre de missions")
    print("augmente, plus le score de performance tend à être élevé.")
elif correlation > 0.4:
    print("Force du lien : modérée entre le nombre de missions et la performance.")
else:
    print("Force du lien : faible ou inexistante entre ces deux variables.")
print("-" * 60 + "\n")

# 3. MODÉLISATION : RÉGRESSION LINÉAIRE SIMPLE
X = df[[X_var]].values
y = df[Y_var].values

modele = LinearRegression()
modele.fit(X, y)

pente = modele.coef_[0]
ordonnee_origine = modele.intercept_
r_deux = modele.score(X, y)

print("--- MODÉLISATION (RÉGRESSION LINÉAIRE) ---")
print(f"Équation de la droite : Score = {pente:.3f} * (Nombre de missions) + {ordonnee_origine:.3f}")
print(f"Coefficient de détermination (R²) : {r_deux:.3f} "
      f"(le modèle explique {r_deux*100:.1f}% de la variance du score)")
print("-" * 60 + "\n")

# 4. LIMITES DE L'ESTIMATION (demandé explicitement par la Question 2)
# On ne peut raisonnablement anticiper le score que dans la plage de missions
# réellement observée : au-delà, on extrapole hors du domaine appris par le
# modèle, ce qui est risqué.
x_min, x_max = df[X_var].min(), df[X_var].max()
residus = y - modele.predict(X)
erreur_type = residus.std()

print("--- LIMITES DE L'ANTICIPATION ---")
print(f"Plage de missions observée dans les données : [{x_min} ; {x_max}]")
print("=> L'estimation du score à partir du nombre de missions n'est raisonnable")
print(f"   QUE pour un freelance situé dans cette plage. En dehors (ex: un tout")
print(f"   nouveau freelance à 0 mission, ou un profil à plus de {x_max} missions),")
print("   le modèle extrapole et devient peu fiable.")
print(f"Erreur type des prédictions : ±{erreur_type:.1f} points de score")
print(f"=> Même dans la plage valide, une estimation individuelle peut s'écarter")
print(f"   du score réel de l'ordre de {erreur_type:.1f} points en moyenne : le R²")
print(f"   de {r_deux:.2f} indique qu'une partie ({100*(1-r_deux):.0f}%) de la performance")
print("   dépend d'autres facteurs non mesurés ici (domaine, expérience...).")
print("-" * 60 + "\n")

# 5. REPRÉSENTATION GRAPHIQUE (Nuage de points + Droite de régression)
plt.figure(figsize=(10, 6))
sns.set_theme(style="whitegrid")

sns.scatterplot(
    data=df,
    x=X_var,
    y=Y_var,
    hue="profil_type",
    palette={"Premium": "#2ecc71", "Standard": "#e74c3c"},
    alpha=0.8,
    s=70,
)

X_droite = np.linspace(x_min, x_max, 100).reshape(-1, 1)
y_droite = modele.predict(X_droite)

plt.plot(
    X_droite,
    y_droite,
    color="#34495e",
    linestyle="--",
    linewidth=2,
    label=f"Modèle Linéaire (R² = {r_deux:.2f})",
)

plt.title(
    "Analyse bivariée : Relation entre le volume d'activité et la performance",
    fontsize=14,
    fontweight="bold",
    pad=15,
)
plt.xlabel("Nombre de missions réalisées", fontsize=12)
plt.ylabel("Score de performance (0-100)", fontsize=12)
plt.legend(title="Légende", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()

output_image = os.path.join(script_dir, "graphique_analyse_bivariee.png")
plt.savefig(output_image, dpi=300)
print(f"Graphique sauvegardé avec succès sous : {output_image}")

plt.show()
