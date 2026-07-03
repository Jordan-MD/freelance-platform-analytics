import numpy as np
from dataset import config
from dataset.models import Freelance

def generate_ml_variables(
    rng: np.random.Generator,
    n: int,
    score_mean: float,
    score_std: float,
    missions_mean: float,
    missions_std: float,
    correlation: float,
) -> tuple[np.ndarray, np.ndarray]:

    mean = [missions_mean, score_mean]
    cov = [
        [missions_std ** 2, correlation * missions_std * score_std],
        [correlation * missions_std * score_std, score_std ** 2],
    ]
    echantillon = rng.multivariate_normal(mean, cov, size=n)

    missions = np.clip(np.round(echantillon[:, 0]), 1, 150).astype(int)
    score = np.clip(np.round(echantillon[:, 1], 1), 0, 100)
    return missions, score


def generate_labels(
    rng: np.random.Generator,
    missions: np.ndarray,
    score: np.ndarray,
    weight_score: float,
    weight_missions: float,
    flip_rate: float,
) -> np.ndarray:

    n = len(score)
    score_norm = (score - score.mean()) / score.std()
    missions_norm = (missions - missions.mean()) / missions.std()

    bruit = rng.normal(0, 1.0, size=n)
    logit = weight_score * score_norm + weight_missions * missions_norm + bruit
    proba_premium = 1 / (1 + np.exp(-logit))
    label = np.where(proba_premium > 0.5, "Premium", "Standard")

    flip_mask = rng.random(n) < flip_rate
    label = label.copy()
    label[flip_mask] = np.where(label[flip_mask] == "Premium", "Standard", "Premium")
    return label


def generate_freelances(rng: np.random.Generator, n: int = config.N) -> list[Freelance]:

    missions, score = generate_ml_variables(
        rng, n,
        config.SCORE_MEAN, config.SCORE_STD,
        config.MISSIONS_MEAN, config.MISSIONS_STD,
        config.CORRELATION,
    )
    labels = generate_labels(
        rng, missions, score,
        config.WEIGHT_SCORE, config.WEIGHT_MISSIONS, config.LABEL_FLIP_RATE,
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
