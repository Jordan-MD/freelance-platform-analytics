import json
import os
from typing import Any


def ensure_dir(path: str) -> None:
    """
    Cree un dossier s'il n'existe pas deja.

    Args:
        path: Chemin du dossier a creer.
    """
    os.makedirs(path, exist_ok=True)


def format_float(value: float, decimals: int = 2) -> str:
    """
    Formate un nombre flottant avec un nombre de decimales fixe.

    Args:
        value: La valeur numerique a formater.
        decimals: Le nombre de decimales souhaite (2 par defaut).

    Returns:
        La valeur formatee sous forme de chaine de caracteres.
    """
    return f"{value:.{decimals}f}"


def export_results_json(results: dict[str, Any], output_path: str) -> None:
    """
    Exporte un dictionnaire de resultats vers un fichier JSON lisible.

    Args:
        results: Dictionnaire contenant les resultats a exporter.
        output_path: Chemin du fichier JSON de sortie.
    """
    ensure_dir(os.path.dirname(output_path) or ".")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False, default=str)


def print_section(title: str) -> None:
    """
    Affiche un titre de section formate dans la console, pour structurer
    la sortie du script principal.

    Args:
        title: Le titre de la section a afficher.
    """
    separator = "=" * 60
    print(f"\n{separator}\n{title}\n{separator}")
