import numpy as np

from dataset import config
from dataset.generator import generate_freelances
from dataset.models import Freelance


def valider(freelances: list[Freelance]) -> tuple[bool, list[str]]:
    erreurs = []

    if len(freelances) != config.N:
        erreurs.append(
            f"nombre de freelances incorrect ({len(freelances)} au lieu de {config.N})"
        )

    ids = [f.id for f in freelances]
    if len(ids) != len(set(ids)):
        erreurs.append("identifiants non uniques")

    if any(f.nombre_mission < 0 for f in freelances):
        erreurs.append("valeur négative détectée (nombre_mission)")

    if any(not (0 <= f.score_performance <= 100) for f in freelances):
        erreurs.append("score_performance hors de la plage 0-100")

    if any(f.id is None or f.profil is None for f in freelances):
        erreurs.append("champ vide détecté")

    profils_presents = {f.profil for f in freelances}
    if "Premium" not in profils_presents:
        erreurs.append("aucun freelance Premium présent")
    if "Standard" not in profils_presents:
        erreurs.append("aucun freelance Standard présent")

    missions = np.array([f.nombre_mission for f in freelances])
    scores = np.array([f.score_performance for f in freelances])
    correlation = float(np.corrcoef(missions, scores)[0, 1])
    if correlation < config.MIN_CORRELATION:
        erreurs.append(
            f"corrélation trop faible ({correlation:.3f}, minimum attendu {config.MIN_CORRELATION:.2f})"
        )

    return (len(erreurs) == 0, erreurs)


def generer_dataset_valide(
    rng: np.random.Generator,
    n: int = config.N,
    max_attempts: int = config.MAX_GENERATION_ATTEMPTS,
) -> tuple[list[Freelance], int]:
    """
    Génère des freelances jusqu'à obtenir un dataset qui passe toutes les
    règles de validation. Retourne (freelances, nombre_de_tentatives).
    """
    for tentative in range(1, max_attempts + 1):
        freelances = generate_freelances(rng, n)
        est_valide, erreurs = valider(freelances)

        if est_valide:
            return freelances, tentative

        print(f"Dataset invalide (tentative {tentative}) : {erreurs}")

    raise RuntimeError(
        f"Impossible d'obtenir un dataset valide après {max_attempts} tentatives."
    )
