from dataclasses import dataclass

@dataclass(frozen=True)
class Freelance:
    id: str
    score_performance: float
    nombre_mission: int
    profil: str
