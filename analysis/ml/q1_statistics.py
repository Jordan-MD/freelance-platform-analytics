from typing import Any

import pandas as pd

from visualization import plot_boxplot, plot_histogram

COLUMN_NAME = "score_performance"


def compute_statistics(df: pd.DataFrame, column: str = COLUMN_NAME) -> dict[str, float]:
    """
    Calcule les indicateurs de statistique descriptive univariee
    pour une colonne donnee.

    Args:
        df: Le DataFrame contenant les donnees.
        column: Le nom de la colonne quantitative a analyser.

    Returns:
        Un dictionnaire contenant moyenne, mediane, mode, variance,
        ecart-type, minimum, maximum et quartiles (Q1, Q3).
    """
    series = df[column]

    return {
        "mean": float(series.mean()),
        "median": float(series.median()),
        "mode": float(series.mode().iloc[0]),
        "variance": float(series.var()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),
        "q1": float(series.quantile(0.25)),
        "q3": float(series.quantile(0.75)),
    }


def detect_outliers(df: pd.DataFrame, column: str = COLUMN_NAME) -> pd.DataFrame:
    """
    Detecte les valeurs atypiques (outliers) selon la regle de l'ecart
    interquartile (IQR), methode standard et robuste pour ce type d'analyse.

    Args:
        df: Le DataFrame contenant les donnees.
        column: Le nom de la colonne quantitative a analyser.

    Returns:
        Un sous-DataFrame contenant uniquement les lignes considerees
        comme atypiques.
    """
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return df[(df[column] < lower_bound) | (df[column] > upper_bound)]


def generate_interpretation(stats: dict[str, float], outliers_count: int) -> str:
    """
    Genere une interpretation automatique, en langage clair, des
    statistiques calculees pour la variable etudiee.

    Args:
        stats: Le dictionnaire de statistiques produit par compute_statistics().
        outliers_count: Le nombre de valeurs atypiques detectees.

    Returns:
        Un texte d'interpretation destine a un lecteur non statisticien.
    """
    dispersion_ratio = stats["std"] / stats["mean"] if stats["mean"] != 0 else 0

    dispersion_comment = (
        "une dispersion relativement faible autour de la moyenne"
        if dispersion_ratio < 0.25
        else "une dispersion notable autour de la moyenne"
    )

    outlier_comment = (
        "aucune valeur ne sort vraiment du lot"
        if outliers_count == 0
        else f"{outliers_count} individu(s) presentent une valeur nettement en dehors de la tendance generale"
    )

    return (
        f"En moyenne, la valeur observee est de {stats['mean']:.2f} "
        f"(mediane : {stats['median']:.2f}), avec {dispersion_comment} "
        f"(ecart-type de {stats['std']:.2f}). Les valeurs s'etendent de "
        f"{stats['min']:.2f} a {stats['max']:.2f}. Sur le plan des cas "
        f"particuliers, {outlier_comment}."
    )


def analyze_q1(df: pd.DataFrame, column: str = COLUMN_NAME) -> dict[str, Any]:
    """
    Execute l'analyse complete de la Question 1 : calcul des statistiques,
    detection des outliers, generation des graphiques et interpretation.

    Args:
        df: Le DataFrame contenant les donnees.
        column: Le nom de la colonne quantitative a analyser.

    Returns:
        Un dictionnaire regroupant statistiques, outliers, chemins des
        graphiques generes et interpretation textuelle.
    """
    stats = compute_statistics(df, column)
    outliers = detect_outliers(df, column)

    histogram_path = plot_histogram(df[column], column)
    boxplot_path = plot_boxplot(df[column], column)

    interpretation = generate_interpretation(stats, len(outliers))

    return {
        "statistics": stats,
        "outliers_count": len(outliers),
        "outliers_ids": outliers["id"].tolist() if "id" in outliers.columns else [],
        "histogram_path": histogram_path,
        "boxplot_path": boxplot_path,
        "interpretation": interpretation,
    }
