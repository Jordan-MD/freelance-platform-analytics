import numpy as np
import pandas as pd

# =============================================================================
# ÉTAPE 1 — GÉNÉRATION DE LA GRAINE À PARTIR DU NOM DU CHEF DE GROUPE
# =============================================================================

def name_to_seed(nom_complet: str) -> int:
    """
    Transforme le nom complet du chef de groupe (nom + prénoms, sans accents ni
    espaces, en majuscules) en une graine entière reproductible.
    """
    chaine = nom_complet.upper().replace(" ", "")
    seed = 0
    for caractere in chaine:
        valeur = ord(caractere) - ord('A') + 1  # A=1, B=2, ..., Z=26
        seed = (seed * 31 + valeur) % (2**32 - 1)
    return seed


NOM_CHEF_GROUPE = "JORDAN BENI MBEZOU DJAMEN"
SEED = name_to_seed(NOM_CHEF_GROUPE)

print(f"Chaîne transformée : {NOM_CHEF_GROUPE.upper().replace(' ', '')}")
print(f"Graine obtenue (SEED) : {SEED}")

rng = np.random.default_rng(SEED)

# =============================================================================
# ÉTAPE 2 — PARAMÈTRES DE GÉNÉRATION
# =============================================================================

sample_size = 80 
PROFILS = {
    "debutant_prometteur": {
        "proportion": 0.40,
        "missions_mean": 8,  "missions_std": 4,
        "score_mean": 62,    "score_std": 12,
    },
    "solide_regulier": {
        "proportion": 0.35,
        "missions_mean": 35, "missions_std": 10,
        "score_mean": 75,    "score_std": 8,
    },
    "veteran_confirme": {
        "proportion": 0.25,
        "missions_mean": 70, "missions_std": 15,
        "score_mean": 88,    "score_std": 6,
    },
}
CORRELATION_INTRA_PROFIL = 0.6  # corrélation positive missions/score DANS chaque profil

DOMAINES = ["Développeur", "Designer", "Rédacteur"]
DOMAINES_PROBA = [0.45, 0.30, 0.25]

# =============================================================================
# ÉTAPE 3 — GÉNÉRATION DES DEUX VARIABLES UTILISÉES DANS LE ML
# =============================================================================

profil_assignments = rng.choice(
    list(PROFILS.keys()), size=sample_size, p=[p["proportion"] for p in PROFILS.values()]
)

nombre_missions = np.zeros(sample_size)
score_performance = np.zeros(sample_size)

for profil_nom, params in PROFILS.items():
    mask = profil_assignments == profil_nom
    n_profil = mask.sum()
    if n_profil == 0:
        continue

    # Génération bivariée corrélée (missions, score) via une gaussienne 2D
    mean = [params["missions_mean"], params["score_mean"]]
    cov = [
        [params["missions_std"] ** 2,
         CORRELATION_INTRA_PROFIL * params["missions_std"] * params["score_std"]],
        [CORRELATION_INTRA_PROFIL * params["missions_std"] * params["score_std"],
         params["score_std"] ** 2],
    ]
    echantillon = rng.multivariate_normal(mean, cov, size=n_profil)
    nombre_missions[mask] = echantillon[:, 0]
    score_performance[mask] = echantillon[:, 1]

# Nettoyage / bornage dans des plages plausibles
nombre_missions = np.clip(np.round(nombre_missions), 1, 150).astype(int)
score_performance = np.clip(np.round(score_performance, 1), 0, 100)

# =============================================================================
# ÉTAPE 4 — ÉTIQUETTE CIBLE : PREMIUM / STANDARD (pour Q4)
# =============================================================================

score_norm = (score_performance - score_performance.mean()) / score_performance.std()
missions_norm = (nombre_missions - nombre_missions.mean()) / nombre_missions.std()

bruit = rng.normal(0, 1.0, size=sample_size)
logit = 1.1 * score_norm + 0.7 * missions_norm + bruit
proba_premium = 1 / (1 + np.exp(-logit))

label = np.where(proba_premium > 0.5, "Premium", "Standard")

# Bruit de classement supplémentaire (erreurs humaines volontaires, ~8%)
flip_mask = rng.random(sample_size) < 0.08
label_flipped = label.copy()
label_flipped[flip_mask] = np.where(label[flip_mask] == "Premium", "Standard", "Premium")
label = label_flipped

# =============================================================================
# ÉTAPE 5 — VARIABLES D'AFFICHAGE (non utilisées dans le ML, juste pour l'appli)
# =============================================================================

domaine = rng.choice(DOMAINES, size=sample_size, p=DOMAINES_PROBA)

# Années d'expérience : corrélée au nombre de missions + bruit
annees_experience = np.clip(
    np.round(nombre_missions / 7 + rng.normal(0, 1.5, size=sample_size), 1), 0.2, 15
)

# Tarif horaire (FCFA/heure) : dépend du domaine (base) + score (prime qualité) + bruit
base_tarif = {"Développeur": 4500, "Designer": 3500, "Rédacteur": 2500}
tarif_horaire = np.array([
    base_tarif[d] + 25 * (s - 50) + rng.normal(0, 400)
    for d, s in zip(domaine, score_performance)
])
tarif_horaire = np.clip(np.round(tarif_horaire, -1), 1000, 15000).astype(int)

# Temps moyen de livraison (jours) : meilleur score -> livraison plus rapide
temps_livraison = np.clip(
    np.round(6 - 0.03 * (score_performance - 50) + rng.normal(0, 1.2, size=sample_size), 1),
    0.5, 15
)

# Taux de réponse (%) : corrélé positivement au score
taux_reponse = np.clip(
    np.round(60 + 0.35 * (score_performance - 50) + rng.normal(0, 8, size=sample_size), 1),
    10, 100
)

# =============================================================================
# ÉTAPE 6 — ASSEMBLAGE DU DATAFRAME FINAL
# =============================================================================

df = pd.DataFrame({
    "id_freelance": [f"FR{str(i+1).zfill(3)}" for i in range(sample_size)],
    "domaine": domaine,
    "annees_experience": annees_experience,
    "nombre_missions": nombre_missions,          # utilisé ML
    "score_performance": score_performance,       # utilisé ML
    "tarif_horaire_fcfa": tarif_horaire,
    "temps_livraison_jours": temps_livraison,
    "taux_reponse_pct": taux_reponse,
    "profil_type": label,                         # cible ML (Premium/Standard)
})

# =============================================================================
# ÉTAPE 7 — VÉRIFICATIONS DE COHÉRENCE (à inclure dans le rapport)
# =============================================================================

print("\n--- Aperçu du jeu de données ---")
print(df.head(10).to_string(index=False))

print("\n--- Statistiques descriptives (variables ML) ---")
print(df[["nombre_missions", "score_performance"]].describe())

print("\n--- Corrélation missions / score (doit être positive) ---")
print(df[["nombre_missions", "score_performance"]].corr())

print("\n--- Répartition des labels ---")
print(df["profil_type"].value_counts())

print("\n--- Répartition des profils latents générés (vérification interne) ---")
print(pd.Series(profil_assignments).value_counts())

# =============================================================================
# ÉTAPE 8 — EXPORT
# =============================================================================

df.to_csv("dataset_freelance_groupe.csv", index=False)
print("\nFichier exporté : dataset_freelance_groupe.csv")
