import io
from typing import Any

import pandas as pd


def run_eda(df: pd.DataFrame) -> dict[str, Any]:
    """
    Effectue une exploration standard du dataset : apercu, structure,
    statistiques descriptives, valeurs manquantes et doublons.

    Args:
        df: Le DataFrame a explorer.

    Returns:
        Un dictionnaire structure contenant :
            - "head": les 5 premieres lignes (DataFrame)
            - "info": le resume technique (str)
            - "describe": les statistiques descriptives (DataFrame)
            - "missing_values": le nombre de valeurs manquantes par colonne
            - "duplicates": le nombre de lignes dupliquees
            - "dtypes": les types de chaque colonne
    """
    buffer = io.StringIO()
    df.info(buf=buffer)

    return {
        "head": df.head(),
        "info": buffer.getvalue(),
        "describe": df.describe(include="all"),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "dtypes": df.dtypes.astype(str).to_dict(),
    }


def print_eda_report(eda_results: dict[str, Any]) -> None:
    """
    Affiche dans la console un rapport lisible des resultats de l'EDA.

    Args:
        eda_results: Le dictionnaire produit par run_eda().
    """
    print("\n--- Apercu des 5 premieres lignes ---")
    print(eda_results["head"])

    print("\n--- Informations structurelles ---")
    print(eda_results["info"])

    print("\n--- Statistiques descriptives globales ---")
    print(eda_results["describe"])

    print("\n--- Valeurs manquantes par colonne ---")
    print(eda_results["missing_values"])

    print("\n--- Lignes dupliquees ---")
    print(eda_results["duplicates"])
