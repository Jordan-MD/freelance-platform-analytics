import csv
from dataclasses import asdict, fields

from dataset.models import Freelance


def export_csv(freelances: list[Freelance], path: str) -> None:
    champs = [f.name for f in fields(Freelance)]
    with open(path, "w", newline="", encoding="utf-8") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=champs)
        writer.writeheader()
        for freelance in freelances:
            writer.writerow(asdict(freelance))
