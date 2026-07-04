import numpy as np
from dataset import config
from dataset.models import Freelance


def generate_missions(
    rng: np.random.Generator,
    n: int,
    missions_mean: float,
    missions_std: float,
    missions_min: int,
    missions_max: int,
) -> np.ndarray:
    """
    Génère le nombre de missions avec une loi normale simple.

    On arrondit pour obtenir des nombres entiers, puis on borne les valeurs
    pour éviter des missions impossibles ou trop extrêmes.
    """
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
    """
    Calcule le score à partir des missions avec une formule linéaire lisible.

    Le bruit gaussien rend les données réalistes : deux freelances avec le
    même nombre de missions ne doivent pas forcément avoir le même score.
    """
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
    """
    Attribue le profil avec une règle simple basée sur un seuil.

    L'indice Premium peut recevoir un bruit configurable. Ensuite, quelques
    étiquettes sont inversées pour éviter une classification parfaite à 100%.
    """
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


def generate_freelances(rng: np.random.Generator, n: int = config.N) -> list[Freelance]:

    missions = generate_missions(
        rng, n,
        config.MISSIONS_MEAN, config.MISSIONS_STD,
        config.MISSIONS_MIN, config.MISSIONS_MAX,
    )
    score = generate_scores(
        rng, missions,
        config.BASE_SCORE, config.MISSION_INFLUENCE,
        config.SCORE_NOISE_STD,
        config.SCORE_MIN, config.SCORE_MAX,
    )
    labels = generate_labels(
        rng, score,
        config.PREMIUM_THRESHOLD, config.PREMIUM_NOISE_STD,
        config.LABEL_FLIP_RATE,
    )

    return [
        Freelance(
            id=f"FR{str(i + 1).zfill(3)}",
            score_performance=float(score[i]),
            nombre_mission=int(missions[i]),
            profil=str(labels[i]),
        )
        for i in range(n)
    ]
