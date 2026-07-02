from dataclasses import dataclass, field
import numpy as np
import pandas as pd

# =============================================================================
# CONFIGURATION — regroupée, séparée de toute logique exécutable
# =============================================================================

@dataclass(frozen=True)
class Profil:
    nom: str
    proportion: float
    missions_mean: float
    missions_std: float
    score_mean: float
    score_std: float


DEFAULT_PROFILS: list[Profil] = [
    Profil("debutant_prometteur", 0.40, missions_mean=8, missions_std=4,
           score_mean=62, score_std=12),
    Profil("solide_regulier", 0.35, missions_mean=35, missions_std=10,
           score_mean=75, score_std=8),
    Profil("veteran_confirme", 0.25, missions_mean=70, missions_std=15,
           score_mean=88, score_std=6),
]

DEFAULT_DOMAINES = ["Développeur", "Designer", "Rédacteur"]
DEFAULT_DOMAINES_PROBA = [0.45, 0.30, 0.25]
DEFAULT_BASE_TARIF = {"Développeur": 4500, "Designer": 3500, "Rédacteur": 2500}

CORRELATION_INTRA_PROFIL = 0.6  # corrélation positive missions/score DANS chaque profil
LABEL_FLIP_RATE = 0.08          # taux d'erreurs volontaires sur l'étiquette (classement "au feeling")
N_DEFAULT = 80


# =============================================================================
# ÉTAPE 1 — GÉNÉRATION DE LA GRAINE
# =============================================================================

def name_to_seed(nom_complet: str) -> int:
    chaine = nom_complet.upper().replace(" ", "")
    seed = 0
    for caractere in chaine:
        valeur = ord(caractere) - ord('A') + 1  # A=1, ..., Z=26
        seed = (seed * 31 + valeur) % (2**32 - 1)
    return seed


# =============================================================================
# ÉTAPE 2 — ASSIGNATION DES PROFILS LATENTS
# =============================================================================

def generate_profile_assignments(
    rng: np.random.Generator, 
    n: int, profils: list[Profil]
) -> np.ndarray:
    noms = [p.nom for p in profils]
    probas = [p.proportion for p in profils]
    return rng.choice(noms, size=n, p=probas)


# =============================================================================
# ÉTAPE 3 — VARIABLES ML (nombre_missions, score_performance)
# =============================================================================

def generate_ml_variables(
    rng: np.random.Generator,
    profile_assignments: np.ndarray,
    profils: list[Profil],
    correlation: float = CORRELATION_INTRA_PROFIL,
) -> tuple[np.ndarray, np.ndarray]:
    n = len(profile_assignments)
    nombre_missions = np.zeros(n)
    score_performance = np.zeros(n)

    for profil in profils:
        mask = profile_assignments == profil.nom
        n_profil = int(mask.sum())
        if n_profil == 0:
            continue

        mean = [profil.missions_mean, profil.score_mean]
        cov = [
            [profil.missions_std ** 2,
             correlation * profil.missions_std * profil.score_std],
            [correlation * profil.missions_std * profil.score_std,
             profil.score_std ** 2],
        ]
        echantillon = rng.multivariate_normal(mean, cov, size=n_profil)
        nombre_missions[mask] = echantillon[:, 0]
        score_performance[mask] = echantillon[:, 1]

    nombre_missions = np.clip(np.round(nombre_missions), 1, 150).astype(int)
    score_performance = np.clip(np.round(score_performance, 1), 0, 100)
    return nombre_missions, score_performance


# =============================================================================
# ÉTAPE 4 — ÉTIQUETTE CIBLE (Premium / Standard)
# =============================================================================

def generate_labels(
    rng: np.random.Generator,
    nombre_missions: np.ndarray,
    score_performance: np.ndarray,
    flip_rate: float = LABEL_FLIP_RATE,
    weight_score: float = 1.1,
    weight_missions: float = 0.7,
) -> np.ndarray:
    n = len(nombre_missions)
    score_norm = (score_performance - score_performance.mean()) / score_performance.std()
    missions_norm = (nombre_missions - nombre_missions.mean()) / nombre_missions.std()

    bruit = rng.normal(0, 1.0, size=n)
    logit = weight_score * score_norm + weight_missions * missions_norm + bruit
    proba_premium = 1 / (1 + np.exp(-logit))
    label = np.where(proba_premium > 0.5, "Premium", "Standard")

    flip_mask = rng.random(n) < flip_rate
    label = label.copy()
    label[flip_mask] = np.where(label[flip_mask] == "Premium", "Standard", "Premium")
    return label


# =============================================================================
# ÉTAPE 5 — VARIABLES D'AFFICHAGE (non utilisées dans le ML)
# =============================================================================

def generate_display_variables(
    rng: np.random.Generator,
    nombre_missions: np.ndarray,
    score_performance: np.ndarray,
    domaines: list[str] = DEFAULT_DOMAINES,
    domaines_proba: list[float] = DEFAULT_DOMAINES_PROBA,
    base_tarif: dict[str, int] = DEFAULT_BASE_TARIF,
) -> dict[str, np.ndarray]:
    """Génère les colonnes de présentation, dérivées des variables ML + bruit."""
    n = len(nombre_missions)
    domaine = rng.choice(domaines, size=n, p=domaines_proba)

    annees_experience = np.clip(
        np.round(nombre_missions / 7 + rng.normal(0, 1.5, size=n), 1), 0.2, 15
    )

    tarif_horaire = np.array([
        base_tarif[d] + 25 * (s - 50) + rng.normal(0, 400)
        for d, s in zip(domaine, score_performance)
    ])
    tarif_horaire = np.clip(np.round(tarif_horaire, -1), 1000, 15000).astype(int)

    temps_livraison = np.clip(
        np.round(6 - 0.03 * (score_performance - 50) + rng.normal(0, 1.2, size=n), 1),
        0.5, 15
    )

    taux_reponse = np.clip(
        np.round(60 + 0.35 * (score_performance - 50) + rng.normal(0, 8, size=n), 1),
        10, 100
    )

    return {
        "domaine": domaine,
        "annees_experience": annees_experience,
        "tarif_horaire_fcfa": tarif_horaire,
        "temps_livraison_jours": temps_livraison,
        "taux_reponse_pct": taux_reponse,
    }


# =============================================================================
# ÉTAPE 6 — ORCHESTRATION : assemble tout, sans I/O
# =============================================================================

def build_dataset(
    nom_chef_groupe: str,
    n: int = N_DEFAULT,
    profils: list[Profil] = None,
) -> tuple[pd.DataFrame, int, np.ndarray]:

    profils = profils or DEFAULT_PROFILS
    seed = name_to_seed(nom_chef_groupe)
    rng = np.random.default_rng(seed)

    profile_assignments = generate_profile_assignments(rng, n, profils)
    nombre_missions, score_performance = generate_ml_variables(
        rng, profile_assignments, profils
    )
    label = generate_labels(rng, nombre_missions, score_performance)
    display_vars = generate_display_variables(rng, nombre_missions, score_performance)

    df = pd.DataFrame({
        "id_freelance": [f"FR{str(i+1).zfill(3)}" for i in range(n)],
        "domaine": display_vars["domaine"],
        "annees_experience": display_vars["annees_experience"],
        "nombre_missions": nombre_missions,          # utilisé ML
        "score_performance": score_performance,       # utilisé ML
        "tarif_horaire_fcfa": display_vars["tarif_horaire_fcfa"],
        "temps_livraison_jours": display_vars["temps_livraison_jours"],
        "taux_reponse_pct": display_vars["taux_reponse_pct"],
        "profil_type": label,                          # cible ML (Premium/Standard)
    })

    return df, seed, profile_assignments


# =============================================================================
# ÉTAPE 7 — VÉRIFICATIONS
# =============================================================================

def compute_diagnostics(df: pd.DataFrame, profile_assignments: np.ndarray) -> dict:
    correlation = df[["nombre_missions", "score_performance"]].corr().iloc[0, 1]
    return {
        "n": len(df),
        "correlation_missions_score": round(float(correlation), 3),
        "label_counts": df["profil_type"].value_counts().to_dict(),
        "profile_counts": pd.Series(profile_assignments).value_counts().to_dict(),
        "score_stats": df["score_performance"].describe().to_dict(),
    }


# =============================================================================
# POINT D'ENTRÉE SCRIPT — Fonction main() pour le test
# =============================================================================

def main() -> None:
    nom_chef_groupe = "JORDAN BENI MBEZOU DJAMEN"
    df, seed, profile_assignments = build_dataset(nom_chef_groupe, n=N_DEFAULT)
    diagnostics = compute_diagnostics(df, profile_assignments)

    print(f"Chaîne transformée : {nom_chef_groupe.upper().replace(' ', '')}")
    print(f"Graine obtenue (SEED) : {seed}")

    print("\n--- Aperçu du jeu de données ---")
    print(df.head(10).to_string(index=False))

    print("\n--- Statistiques descriptives (variables ML) ---")
    print(df[["nombre_missions", "score_performance"]].describe())

    print(f"\n--- Corrélation missions / score : {diagnostics['correlation_missions_score']} ---")
    print(f"--- Répartition des labels : {diagnostics['label_counts']} ---")
    print(f"--- Répartition des profils latents (vérification interne) : {diagnostics['profile_counts']} ---")

    df.to_csv("dataset_freelance_groupe.csv", index=False)
    print("\nFichier exporté : dataset_freelance_groupe.csv")


if __name__ == "__main__":
    main()