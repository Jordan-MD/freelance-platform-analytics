from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from visualization import plot_scatter

X_COLUMN = "nombre_mission"
Y_COLUMN = "score_performance"


def compute_correlation(
    df: pd.DataFrame, x_column: str = X_COLUMN, y_column: str = Y_COLUMN
) -> dict[str, float]:
    """
    Calcule le coefficient de correlation de Pearson entre deux variables
    quantitatives, ainsi que la droite de regression lineaire associee.

    Args:
        df: Le DataFrame contenant les donnees.
        x_column: Le nom de la variable explicative.
        y_column: Le nom de la variable expliquee.

    Returns:
        Un dictionnaire contenant le coefficient r, la p-value, le
        coefficient de determination r carre, la pente et l'ordonnee a l'origine.
    """
    x = df[x_column].to_numpy(dtype=float)
    y = df[y_column].to_numpy(dtype=float)

    r, p_value = pearsonr(x, y)
    slope, intercept = np.polyfit(x, y, deg=1)

    return {
        "pearson_r": float(r),
        "p_value": float(p_value),
        "r_squared": float(r**2),
        "slope": float(slope),
        "intercept": float(intercept),
    }


def generate_interpretation(correlation: dict[str, float]) -> str:
    """
    Genere une interpretation automatique, en langage clair, de la
    correlation calculee, incluant une evaluation de la fiabilite
    d'une estimation basee sur cette relation.

    Args:
        correlation: Le dictionnaire produit par compute_correlation().

    Returns:
        Un texte d'interpretation destine a un lecteur non statisticien.
    """
    r = correlation["pearson_r"]
    abs_r = abs(r)
    significant = correlation["p_value"] < 0.05

    if abs_r >= 0.7:
        strength = "forte"
    elif abs_r >= 0.4:
        strength = "moderee"
    elif abs_r >= 0.2:
        strength = "faible"
    else:
        strength = "quasi nulle"

    direction = "positive" if r > 0 else "negative"
    significance_comment = (
        "cette relation est statistiquement significative"
        if significant
        else "cette relation n'est toutefois pas statistiquement significative, "
        "ce qui appelle a la prudence"
    )

    reliability_comment = (
        "une estimation de l'une a partir de l'autre semble raisonnable, "
        "mais uniquement dans la plage de valeurs observees, et avec une marge d'erreur a considerer"
        if abs_r >= 0.5 and significant
        else "une estimation basee uniquement sur cette relation serait risquee "
        "et manquerait de fiabilite"
    )

    return (
        f"La correlation observee entre les deux variables est {strength} "
        f"et {direction} (r = {r:.2f}), et {significance_comment}. "
        f"Le coefficient de determination indique que {correlation['r_squared'] * 100:.1f}% "
        f"de la variation d'une variable est expliquee par l'autre. En consequence, "
        f"{reliability_comment}."
    )


def analyze_q2(
    df: pd.DataFrame, x_column: str = X_COLUMN, y_column: str = Y_COLUMN
) -> dict[str, Any]:
    """
    Execute l'analyse complete de la Question 2 : calcul de la correlation,
    generation du nuage de points avec droite de regression, et
    interpretation.

    Args:
        df: Le DataFrame contenant les donnees.
        x_column: Le nom de la variable explicative.
        y_column: Le nom de la variable expliquee.

    Returns:
        Un dictionnaire regroupant les resultats de correlation, le chemin
        du graphique genere et l'interpretation textuelle.
    """
    correlation = compute_correlation(df, x_column, y_column)

    scatter_path = plot_scatter(
        x=df[x_column],
        y=df[y_column],
        x_label=x_column,
        y_label=y_column,
        slope=correlation["slope"],
        intercept=correlation["intercept"],
    )

    interpretation = generate_interpretation(correlation)

    return {
        "correlation": correlation,
        "scatter_path": scatter_path,
        "interpretation": interpretation,
    }
