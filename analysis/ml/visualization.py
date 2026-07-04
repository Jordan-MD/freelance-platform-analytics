import os
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from utils import ensure_dir

FIGURES_DIR = "figures"


def plot_histogram(
    data: Sequence[float],
    column_name: str,
    output_filename: str = "q1_histogram.png",
) -> str:
    """
    Trace un histogramme de distribution d'une variable quantitative.

    Args:
        data: Les valeurs de la variable a representer.
        column_name: Le nom de la variable (utilise pour le titre et l'axe X).
        output_filename: Le nom du fichier image de sortie.

    Returns:
        Le chemin complet du fichier image genere.
    """
    ensure_dir(FIGURES_DIR)
    output_path = os.path.join(FIGURES_DIR, output_filename)

    plt.figure(figsize=(8, 5))
    plt.hist(data, bins=15, color="#4C72B0", edgecolor="black", alpha=0.85)
    plt.title(f"Distribution de {column_name}")
    plt.xlabel(column_name)
    plt.ylabel("Effectif")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def plot_boxplot(
    data: Sequence[float],
    column_name: str,
    output_filename: str = "q1_boxplot.png",
) -> str:
    """
    Trace une boite a moustaches pour visualiser la dispersion et les
    valeurs atypiques d'une variable quantitative.

    Args:
        data: Les valeurs de la variable a representer.
        column_name: Le nom de la variable.
        output_filename: Le nom du fichier image de sortie.

    Returns:
        Le chemin complet du fichier image genere.
    """
    ensure_dir(FIGURES_DIR)
    output_path = os.path.join(FIGURES_DIR, output_filename)

    plt.figure(figsize=(6, 5))
    plt.boxplot(
        data,
        vert=True,
        patch_artist=True,
        boxprops=dict(facecolor="#DD8452", alpha=0.8),
    )
    plt.title(f"Boite a moustaches - {column_name}")
    plt.ylabel(column_name)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def plot_scatter(
    x: Sequence[float],
    y: Sequence[float],
    x_label: str,
    y_label: str,
    slope: float,
    intercept: float,
    output_filename: str = "q2_scatter.png",
) -> str:
    """
    Trace un nuage de points entre deux variables avec la droite de
    regression lineaire superposee.

    Args:
        x: Valeurs de la variable explicative.
        y: Valeurs de la variable expliquee.
        x_label: Nom de la variable en abscisse.
        y_label: Nom de la variable en ordonnee.
        slope: Pente de la droite de regression.
        intercept: Ordonnee a l'origine de la droite de regression.
        output_filename: Le nom du fichier image de sortie.

    Returns:
        Le chemin complet du fichier image genere.
    """
    ensure_dir(FIGURES_DIR)
    output_path = os.path.join(FIGURES_DIR, output_filename)

    x_arr = np.array(x)
    y_arr = np.array(y)
    line_x = np.linspace(x_arr.min(), x_arr.max(), 100)
    line_y = slope * line_x + intercept

    plt.figure(figsize=(8, 5))
    plt.scatter(x_arr, y_arr, alpha=0.6, color="#4C72B0", label="Observations")
    plt.plot(line_x, line_y, color="#C44E52", linewidth=2, label="Regression lineaire")
    plt.title(f"{y_label} en fonction de {x_label}")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def plot_clusters(
    x: Sequence[float],
    y: Sequence[float],
    labels: Sequence[int],
    centers: np.ndarray,
    x_label: str,
    y_label: str,
    output_filename: str = "q3_clusters.png",
) -> str:
    """
    Trace la repartition des individus par cluster, avec les centres
    des clusters mis en evidence.

    Args:
        x: Valeurs de la premiere variable utilisee pour le clustering.
        y: Valeurs de la seconde variable utilisee pour le clustering.
        labels: Etiquette de cluster attribuee a chaque individu.
        centers: Coordonnees des centres de clusters (dans l'espace original).
        x_label: Nom de la premiere variable.
        y_label: Nom de la seconde variable.
        output_filename: Le nom du fichier image de sortie.

    Returns:
        Le chemin complet du fichier image genere.
    """
    ensure_dir(FIGURES_DIR)
    output_path = os.path.join(FIGURES_DIR, output_filename)

    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(x, y, c=labels, cmap="viridis", alpha=0.7, s=50)
    plt.scatter(
        centers[:, 0],
        centers[:, 1],
        c="red",
        marker="X",
        s=200,
        edgecolor="black",
        label="Centres",
    )
    plt.title("Clustering K-Means des profils")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.colorbar(scatter, label="Cluster")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def plot_confusion_matrix(
    matrix: np.ndarray,
    class_labels: Sequence[str],
    output_filename: str = "q4_confusion_matrix.png",
) -> str:
    """
    Trace une matrice de confusion sous forme de heatmap annotee.

    Args:
        matrix: La matrice de confusion (resultat de sklearn confusion_matrix).
        class_labels: Les noms des classes, dans l'ordre utilise par la matrice.
        output_filename: Le nom du fichier image de sortie.

    Returns:
        Le chemin complet du fichier image genere.
    """
    ensure_dir(FIGURES_DIR)
    output_path = os.path.join(FIGURES_DIR, output_filename)

    matrix = np.array(matrix)

    plt.figure(figsize=(6, 5))
    plt.imshow(matrix, cmap="Blues")
    plt.title("Matrice de confusion - Prediction du profil")
    plt.colorbar()
    tick_positions = np.arange(len(class_labels))
    plt.xticks(tick_positions, class_labels, rotation=45)
    plt.yticks(tick_positions, class_labels)
    plt.xlabel("Predit")
    plt.ylabel("Reel")

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            plt.text(
                j,
                i,
                str(matrix[i, j]),
                ha="center",
                va="center",
                color="white" if matrix[i, j] > matrix.max() / 2 else "black",
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path
