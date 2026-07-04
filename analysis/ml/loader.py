import os

import pandas as pd

REQUIRED_COLUMNS: list[str] = ["id", "score_performance", "nombre_mission", "profil"]


def load_dataset(csv_path: str) -> pd.DataFrame:
    """
    Charge le dataset depuis un fichier CSV et verifie sa validite.

    Args:
        csv_path: Chemin vers le fichier CSV contenant les donnees generees.

    Returns:
        Un DataFrame pandas contenant les donnees validees.

    Raises:
        FileNotFoundError: si le fichier n'existe pas a l'emplacement indique.
        ValueError: si une ou plusieurs colonnes attendues sont absentes.
    """
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(
            f"Le fichier '{csv_path}' est introuvable. "
            "Verifiez le chemin fourni vers votre dataset genere."
        )

    df = pd.read_csv(csv_path)
    _validate_columns(df)
    return df


def _validate_columns(df: pd.DataFrame) -> None:
    """
    Verifie que toutes les colonnes requises sont presentes dans le DataFrame.

    Args:
        df: Le DataFrame a valider.

    Raises:
        ValueError: si une colonne requise est manquante.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Colonnes manquantes dans le dataset : {missing}. "
            f"Colonnes attendues : {REQUIRED_COLUMNS}."
        )
