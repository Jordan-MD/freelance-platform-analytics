from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from visualization import plot_clusters

FEATURES = ["score_performance", "nombre_mission"]
FINAL_N_CLUSTERS = 3


def prepare_features(df: pd.DataFrame, features: list[str] = FEATURES) -> np.ndarray:
    """
    Selectionne et normalise les variables utilisees pour le clustering,
    afin de mettre les deux variables sur une echelle comparable.

    Args:
        df: Le DataFrame contenant les donnees.
        features: La liste des colonnes a utiliser pour le clustering.

    Returns:
        Un tableau numpy des variables normalisees (moyenne 0, ecart-type 1).
    """
    scaler = StandardScaler()
    return scaler.fit_transform(df[features])


def compute_elbow_scores(scaled_data: np.ndarray, max_k: int = 8) -> dict[int, float]:
    """
    Calcule l'inertie intra-cluster pour differentes valeurs de k,
    afin d'appliquer la methode du coude et justifier le choix du
    nombre de clusters.

    Args:
        scaled_data: Les donnees normalisees.
        max_k: Le nombre maximal de clusters a tester.

    Returns:
        Un dictionnaire {k: inertie} pour k allant de 2 a max_k.
    """
    inertias = {}
    for k in range(2, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        model.fit(scaled_data)
        inertias[k] = float(model.inertia_)
    return inertias


def compute_silhouette_scores(scaled_data: np.ndarray, max_k: int = 8) -> dict[int, float]:
    """
    Calcule le score de silhouette pour differentes valeurs de k,
    utilise en complement de la methode du coude pour valider le
    nombre de clusters retenu.

    Args:
        scaled_data: Les donnees normalisees.
        max_k: Le nombre maximal de clusters a tester.

    Returns:
        Un dictionnaire {k: score de silhouette} pour k allant de 2 a max_k.
    """
    scores = {}
    for k in range(2, max_k + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(scaled_data)
        scores[k] = float(silhouette_score(scaled_data, labels))
    return scores


def run_kmeans(
    scaled_data: np.ndarray, n_clusters: int = FINAL_N_CLUSTERS
) -> tuple[np.ndarray, np.ndarray]:
    """
    Applique l'algorithme KMeans avec le nombre de clusters retenu.

    Args:
        scaled_data: Les donnees normalisees.
        n_clusters: Le nombre de clusters a former.

    Returns:
        Un tuple (labels, centres) ou labels est l'etiquette de cluster
        attribuee a chaque individu, et centres les coordonnees des
        centres de clusters (dans l'espace normalise).
    """
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(scaled_data)
    return labels, model.cluster_centers_


def generate_interpretation(
    df: pd.DataFrame, labels: np.ndarray, features: list[str] = FEATURES
) -> str:
    """
    Genere une interpretation automatique des profils identifies par
    le clustering, en decrivant chaque groupe par ses moyennes.

    Args:
        df: Le DataFrame original contenant les donnees.
        labels: Les etiquettes de cluster attribuees a chaque individu.
        features: Les colonnes utilisees pour caracteriser les clusters.

    Returns:
        Un texte d'interpretation decrivant chaque profil identifie.
    """
    temp_df = df.copy()
    temp_df["cluster"] = labels

    lines = [f"L'analyse fait ressortir {len(set(labels))} profils distincts :"]
    for cluster_id, group in temp_df.groupby("cluster"):
        means = group[features].mean()
        description = ", ".join(f"{col} moyen de {means[col]:.2f}" for col in features)
        lines.append(f"- Profil {cluster_id} ({len(group)} individus) : {description}.")

    return "\n".join(lines)


def analyze_q3(df: pd.DataFrame, features: list[str] = FEATURES) -> dict[str, Any]:
    """
    Execute l'analyse complete de la Question 3 : normalisation,
    methode du coude, score de silhouette, clustering KMeans final,
    generation du graphique et interpretation.

    Args:
        df: Le DataFrame contenant les donnees.
        features: Les colonnes a utiliser pour le clustering.

    Returns:
        Un dictionnaire regroupant les scores du coude, les scores de
        silhouette, les centres, les effectifs, le chemin du graphique
        et l'interpretation textuelle.
    """
    scaled_data = prepare_features(df, features)

    elbow_scores = compute_elbow_scores(scaled_data)
    silhouette_scores = compute_silhouette_scores(scaled_data)

    labels, centers_scaled = run_kmeans(scaled_data, FINAL_N_CLUSTERS)

    scaler = StandardScaler().fit(df[features])
    centers_original = scaler.inverse_transform(centers_scaled)

    cluster_path = plot_clusters(
        x=df[features[0]],
        y=df[features[1]],
        labels=labels,
        centers=centers_original,
        x_label=features[0],
        y_label=features[1],
    )

    unique, counts = np.unique(labels, return_counts=True)
    effectifs = dict(zip(unique.tolist(), counts.tolist()))

    interpretation = generate_interpretation(df, labels, features)

    return {
        "elbow_scores": elbow_scores,
        "silhouette_scores": silhouette_scores,
        "n_clusters": FINAL_N_CLUSTERS,
        "centers": centers_original.tolist(),
        "effectifs": effectifs,
        "cluster_path": cluster_path,
        "interpretation": interpretation,
    }
