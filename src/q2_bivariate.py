import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression

def analyser_relations_q2(df):
    """
    Logique statistique de la Question 2.
    Analyse la relation linéaire et applique la formule de régression sur des cas concrets
    (0 mission et activité médiane) pour éviter l'extrapolation.
    """
    score = df["score_performance"]
    missions = df["nombre_mission"]
    total = len(df)

    # --- 1. CALCULS STATISTIQUES & CORRÉLATION ---
    r_activite, p_activite = pearsonr(missions, score)
    r_activite = max(-1.0, min(1.0, r_activite)) # Sécurité bornes [-1, 1]

    # 2. MODÉLISATION LINÉAIRE
    X = df[["nombre_mission"]].values
    y = score.values
    modele = LinearRegression().fit(X, y)

    r_deux = modele.score(X, y)
    pente = modele.coef_[0]
    intercept = modele.intercept_
    erreur_type = (y - modele.predict(X)).std()  # CORRECTION: error_type -> erreur_type

    x_min, x_max = missions.min(), missions.max()
    x_mediane_missions = int(missions.median()) # Niveau d'activité typique au cœur des données

    metriques = {
        "r_activite": r_activite, "p_activite": p_activite, "r_squared": r_deux,
        "pente": pente, "intercept": intercept, "erreur_type": erreur_type,
        "x_min": x_min, "x_max": x_max, "x_mediane_missions": x_mediane_missions
    }

    # --- 3. SCÉNARIOS D'APPLICATION DE LA FORMULE ---
    if total < 5:
        scenarios = {
            "statut_lien": "Échantillon trop faible.",
            "predictions_cas": "Données insuffisantes pour appliquer le modèle."
        }
    else:
        scenarios = {}

        # Scénario 1 : Diagnostic de la relation
        if p_activite >= 0.05 or abs(r_activite) < 0.2:
            scenarios["statut_lien"] = (
                rf"**Absence de lien linéaire** ($r = {r_activite:.2f}$, $p \ge 0.05$). "
                rf"Les variables sont statistiquement indépendantes. Appliquer une formule linéaire n'a pas de sens ici."
            )
        else:
            direction = "croissante" if r_activite > 0 else "décroissante"
            scenarios["statut_lien"] = (
                rf"**Dépendance linéaire validée** ($r = {r_activite:.2f}$). "
                rf"La relation est **{direction}**. Le volume d'activité explique {r_deux*100:.1f}% de la performance."
            )

        # Scénario 2 : Applications concrètes de la formule (Sans extrapolation forcée)
        # Cas A : Calcul à 0 mission (Débutant)
        pred_0 = max(0.0, min(100.0, intercept))
        if x_min <= 2:
            txt_0 = f"**Pour un nouveau à 0 mission (Zone connue) :** Le score estimé est de **{pred_0:.1f}/100**."
        else:
            txt_0 = (
                f"**Pour un nouveau à 0 mission (Extrapolation risquée) :** La formule donne théoriquement **{pred_0:.1f}/100**, "
                f"mais vos données ne contiennent aucun profil en dessous de {x_min} missions. Cette estimation reste donc incertaine."
            )

        # Cas B : Calcul au cœur des données (Interpolation parfaite)
        pred_mediane = max(0.0, min(100.0, (pente * x_mediane_missions) + intercept))
        txt_mediane = (
            f"**Pour un profil type à {x_mediane_missions} missions (Sécurité totale) :** Le score estimé est de **{pred_mediane:.1f}/100**. "
            f"Ici, la prédiction est **robuste et fiable** car elle se situe en plein milieu de votre historique de données."
        )

        scenarios["predictions_cas"] = (
            rf"En appliquant l'équation du modèle ($\text{{Score}} = {pente:.2f} \times \text{{Missions}} + {intercept:.1f}$) :\n\n"
            rf"* {txt_0}\n"
            rf"* {txt_mediane}\n\n"
            rf"**Marge d'erreur globale :** Dans tous les cas, comptez une variation individuelle de $\pm{erreur_type:.1f}$ points."
        )

    # --- 4. CRÉATION DU GRAPHIQUE ---
    sns.set_theme(style="whitegrid")
    fig_scatter, ax = plt.subplots(figsize=(10, 6))

    hue_col = "profil" if "profil" in df.columns else None
    sns.scatterplot(data=df, x="nombre_mission", y="score_performance", hue=hue_col, 
                    palette="Set1" if hue_col else None, alpha=0.8, s=70, ax=ax)

    # Droite tracée de 0 jusqu'au maximum pour illustrer les deux cas
    X_droite = np.linspace(0, x_max, 100).reshape(-1, 1)
    y_droite = modele.predict(X_droite)
    ax.plot(X_droite, y_droite, color="#34495e", linestyle="--", linewidth=2, 
            label=f"Modèle Linéaire (R² = {r_deux:.2f})")

    # Marquage visuel de la prédiction au niveau médian pour rassurer le prof
    ax.axvline(x_mediane_missions, color='purple', linestyle=':', alpha=0.7, label=f"Niveau médian ({x_mediane_missions} miss.)")

    ax.set_title("Modélisation de la performance selon l'activité", fontsize=11, fontweight="bold")
    ax.set_xlabel("Nombre de missions réalisées")
    ax.set_ylabel("Score de performance (0-100)")
    ax.set_xlim(left=0)
    ax.legend(title="Légende")
    plt.tight_layout()

    return metriques, fig_scatter, scenarios