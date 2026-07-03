NOM_CHEF_GROUPE = "JORDAN BENI MBEZOU DJAMEN"
N = 80  # taille de l'échantillon

# --- Distribution des variables ML (population unique, pas de profils latents pour l'instant) ---
SCORE_MEAN = 70.0
SCORE_STD = 15.0
MISSIONS_MEAN = 35.0
MISSIONS_STD = 20.0
CORRELATION = 0.7  # corrélation positive missions/score

# --- Génération de l'étiquette Premium/Standard ---
WEIGHT_SCORE = 1.1
WEIGHT_MISSIONS = 0.7
LABEL_FLIP_RATE = 0.08  # ~8% d'erreurs volontaires (classement "au feeling")

# --- Validation / régénération ---
MAX_GENERATION_ATTEMPTS = 100

# --- Export ---
CSV_PATH = "dataset_freelance_groupe.csv"
