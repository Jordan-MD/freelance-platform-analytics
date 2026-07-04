NOM_CHEF_GROUPE = "JORDAN BENI MBEZOU DJAMEN"
N = 80  # taille de l'échantillon

# --- Nombre de missions ---
MISSIONS_MEAN = 45.0
MISSIONS_STD = 22.0
MISSIONS_MIN = 1
MISSIONS_MAX = 150

# --- Score de performance ---
BASE_SCORE = 36.0
MISSION_INFLUENCE = 0.75
SCORE_NOISE_STD = 15.0
SCORE_MIN = 0
SCORE_MAX = 100

# --- Profil Premium/Standard ---
PREMIUM_THRESHOLD = 69.0
PREMIUM_NOISE_STD = 0.5
LABEL_FLIP_RATE = 0.08  # ~8% d'erreurs volontaires

# --- Validation / régénération ---
MIN_CORRELATION = 0.60
MAX_GENERATION_ATTEMPTS = 100

# --- Export ---
CSV_PATH = "dataset/dataset_freelance_groupe.csv"
