from __future__ import annotations

import csv
import unicodedata
from dataclasses import asdict, dataclass, fields
from pathlib import Path

import numpy as np # type: ignore

# --- Configuration constants ---
NOM_CHEF_GROUPE = "JORDAN BENI MBEZOU DJAMEN"
N = 80  # nombre total de freelances à générer

MISSIONS_MEAN = 45.0
MISSIONS_STD = 22.0
MISSIONS_MIN = 1
MISSIONS_MAX = 150

BASE_SCORE = 36.0
MISSION_INFLUENCE = 0.75
SCORE_NOISE_STD = 15.0
SCORE_MIN = 0
SCORE_MAX = 100

PREMIUM_THRESHOLD = 69.0
PREMIUM_NOISE_STD = 0.5
LABEL_FLIP_RATE = 0.08

MIN_CORRELATION = 0.60
MAX_GENERATION_ATTEMPTS = 100
CSV_FILENAME = "dataset_freelance_groupe.csv"


@dataclass(frozen=True)
class Freelance:
    """Data container for a single freelance entry."""

    id: str
    score_performance: float
    nombre_mission: int
    profil: str


def generer_graine_groupe(nom_complet: str) -> int:
    """Convertit un nom en graine déterministe pour la génération pseudo-aléatoire."""
    chaine_normalisee = unicodedata.normalize("NFKD", nom_complet)
    texte_sans_accents = "".join(
        c for c in chaine_normalisee if not unicodedata.combining(c)
    )
    texte_sans_espaces = texte_sans_accents.upper().replace(" ", "")

    p = 31
    m = 2**31 - 1
    graine = 0
    for caractere in texte_sans_espaces:
        graine = (graine * p + ord(caractere)) % m

    return graine


def generate_missions(
    rng: np.random.Generator,
    n: int,
    missions_mean: float,
    missions_std: float,
    missions_min: int,
    missions_max: int,
) -> np.ndarray:
    """Génère un vecteur de nombre de missions pour chaque freelance."""
    missions = rng.normal(missions_mean, missions_std, size=n)
    missions = np.round(missions)
    missions = np.clip(missions, missions_min, missions_max)
    return missions.astype(int)


def generate_scores(
    rng: np.random.Generator,
    missions: np.ndarray,
    base_score: float,
    mission_influence: float,
    noise_std: float,
    score_min: int,
    score_max: int,
) -> np.ndarray:
    """Calcule un score de performance à partir du nombre de missions et d'un bruit aléatoire."""
    bruit = rng.normal(0, noise_std, size=len(missions))
    score = base_score + missions * mission_influence + bruit
    score = np.clip(score, score_min, score_max)
    return np.round(score, 1)


def generate_labels(
    rng: np.random.Generator,
    score: np.ndarray,
    threshold: float,
    noise_std: float,
    flip_rate: float,
) -> np.ndarray:
    """Attribue un profil Premium ou Standard en fonction du score et d'un peu de bruit."""
    n = len(score)
    indice_premium = score + rng.normal(0, noise_std, size=n)
    label = np.where(indice_premium >= threshold, "Premium", "Standard")

    nombre_erreurs = round(n * flip_rate)
    indices_erreurs = rng.choice(n, size=nombre_erreurs, replace=False)
    label = label.copy()
    label[indices_erreurs] = np.where(
        label[indices_erreurs] == "Premium",
        "Standard",
        "Premium",
    )
    return label


def generate_freelances(
    rng: np.random.Generator,
    n: int = N,
) -> list[Freelance]:
    """Construit une liste de freelances en combinant missions, scores et profils."""
    missions = generate_missions(
        rng,
        n,
        MISSIONS_MEAN,
        MISSIONS_STD,
        MISSIONS_MIN,
        MISSIONS_MAX,
    )
    scores = generate_scores(
        rng,
        missions,
        BASE_SCORE,
        MISSION_INFLUENCE,
        SCORE_NOISE_STD,
        SCORE_MIN,
        SCORE_MAX,
    )
    labels = generate_labels(
        rng,
        scores,
        PREMIUM_THRESHOLD,
        PREMIUM_NOISE_STD,
        LABEL_FLIP_RATE,
    )

    return [
        Freelance(
            id=f"FR{str(i + 1).zfill(3)}",
            score_performance=float(scores[i]),
            nombre_mission=int(missions[i]),
            profil=str(labels[i]),
        )
        for i in range(n)
    ]


def valider(freelances: list[Freelance]) -> tuple[bool, list[str]]:
    """Vérifie la validité du dataset généré selon des règles métiers."""
    erreurs: list[str] = []

    if len(freelances) != N:
        erreurs.append(
            f"nombre de freelances incorrect ({len(freelances)} au lieu de {N})"
        )

    ids = [freelance.id for freelance in freelances]
    if len(ids) != len(set(ids)):
        erreurs.append("identifiants non uniques")

    if any(freelance.nombre_mission < 0 for freelance in freelances):
        erreurs.append("valeur négative détectée (nombre_mission)")

    if any(not (0 <= freelance.score_performance <= 100) for freelance in freelances):
        erreurs.append("score_performance hors de la plage 0-100")

    if any(freelance.id is None or freelance.profil is None for freelance in freelances):
        erreurs.append("champ vide détecté")

    profils_presents = {freelance.profil for freelance in freelances}
    if "Premium" not in profils_presents:
        erreurs.append("aucun freelance Premium présent")
    if "Standard" not in profils_presents:
        erreurs.append("aucun freelance Standard présent")

    missions = np.array([freelance.nombre_mission for freelance in freelances])
    scores = np.array([freelance.score_performance for freelance in freelances])
    correlation = float(np.corrcoef(missions, scores)[0, 1])
    if correlation < MIN_CORRELATION:
        erreurs.append(
            f"corrélation trop faible ({correlation:.3f}, minimum attendu {MIN_CORRELATION:.2f})"
        )

    return len(erreurs) == 0, erreurs


def generer_dataset_valide(
    rng: np.random.Generator,
    n: int = N,
    max_attempts: int = MAX_GENERATION_ATTEMPTS,
) -> tuple[list[Freelance], int]:
    """Génère des freelances jusqu'à ce que la validation réussisse."""
    for tentative in range(1, max_attempts + 1):
        freelances = generate_freelances(rng, n)
        est_valide, erreurs = valider(freelances)
        if est_valide:
            return freelances, tentative

        print(f"Dataset invalide (tentative {tentative}) : {erreurs}")

    raise RuntimeError(
        f"Impossible d'obtenir un dataset valide après {max_attempts} tentatives."
    )


def export_csv(freelances: list[Freelance], path: Path) -> None:
    """Export le dataset au format CSV en respectant l'ordre des champs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    champs = [field.name for field in fields(Freelance)]
    with path.open("w", newline="", encoding="utf-8") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=champs)
        writer.writeheader()
        for freelance in freelances:
            writer.writerow(asdict(freelance))


def main() -> None:
    """Point d'entrée du script : génère le dataset et l'exporte en CSV."""
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / CSV_FILENAME

    graine = generer_graine_groupe(NOM_CHEF_GROUPE)
    rng = np.random.default_rng(graine)

    freelances, tentatives = generer_dataset_valide(rng, N)

    missions = [f.nombre_mission for f in freelances]
    scores = [f.score_performance for f in freelances]
    correlation = float(np.corrcoef(missions, scores)[0, 1])
    premium_count = sum(1 for f in freelances if f.profil == "Premium")
    standard_count = sum(1 for f in freelances if f.profil == "Standard")

    print(f"Nom transformé : {NOM_CHEF_GROUPE}")
    print(f"Graine obtenue : {graine}")
    print(f"Dataset valide obtenu en {tentatives} tentative(s)")
    print(f"Nombre de freelances générés : {len(freelances)}")
    print(f"Corrélation missions/score : {correlation:.3f}")
    print(f"Répartition : {premium_count} Premium / {standard_count} Standard")
    print(f"Fichier exporté : {csv_path}")

    export_csv(freelances, csv_path)


if __name__ == "__main__":
    main()
