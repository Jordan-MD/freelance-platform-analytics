import os
import sys
import numpy as np

# Ajouter le dossier parent au chemin de recherche pour permettre les imports absolus
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dataset import config
from dataset.seed import generer_graine_groupe
from dataset.validator import generer_dataset_valide
from dataset.exporter import export_csv


def main() -> None:
    graine = generer_graine_groupe(config.NOM_CHEF_GROUPE)
    rng = np.random.default_rng(graine)

    freelances, tentatives = generer_dataset_valide(rng, config.N)

    print(f"Nom transformé : {config.NOM_CHEF_GROUPE}")
    print(f"Graine obtenue : {graine}")
    print(f"Dataset valide obtenu en {tentatives} tentative(s)")
    print(f"Nombre de freelances générés : {len(freelances)}")

    missions = [f.nombre_mission for f in freelances]
    scores = [f.score_performance for f in freelances]
    correlation = float(np.corrcoef(missions, scores)[0, 1])
    premium_count = sum(1 for f in freelances if f.profil == "Premium")
    standard_count = sum(1 for f in freelances if f.profil == "Standard")

    print(f"Corrélation missions/score : {correlation:.3f}")
    print(f"Répartition : {premium_count} Premium / {standard_count} Standard")

    export_csv(freelances, config.CSV_PATH)
    print(f"Fichier exporté : {config.CSV_PATH}")


if __name__ == "__main__":
    main()
