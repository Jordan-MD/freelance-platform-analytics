import matplotlib.pyplot as plt
import seaborn as sns

def analyser_performance_q1(df):
    """
    Contient uniquement la logique statistique de la Question 1.
    Prend en entrée un DataFrame 'df' et retourne les métriques,
    les graphiques séparés et l'interprétation automatisée.
    """
    score = df["score_performance"]
    total_freelances = len(df)

    # --- 1. CALCULS STATISTIQUES ---
    moyenne = score.mean()
    mediane = score.median()
    ecart_type = score.std()
    min_val = score.min()
    max_val = score.max()

    # --- 1b. Z-SCORE PAR FREELANCE ---
    z_scores = (score - moyenne) / ecart_type
    outliers_zscore = df[abs(z_scores) > 3]

    # --- 2. DÉTECTION DES CAS EXTRÊMES (IQR) ---
    Q1 = score.quantile(0.25)
    Q3 = score.quantile(0.75)
    IQR = Q3 - Q1
    limite_basse = Q1 - 1.5 * IQR
    limite_haute = Q3 + 1.5 * IQR

    cas_extremes = df[(score < limite_basse) | (score > limite_haute)]

    # Dictionnaire des résultats numériques pour l'interface
    metriques = {
        "total": total_freelances,
        "moyenne": moyenne,
        "mediane": mediane,
        "ecart_type": ecart_type,
        "min": min_val,
        "max": max_val,
        "iqr": IQR,
        "nb_outliers": len(cas_extremes),
        "z_scores": z_scores,
        "nb_outliers_zscore": len(outliers_zscore),
    }

    # --- 3. LOGIQUE D'INTERPRÉTATION AUTOMATIQUE (Cas limites) ---
    # Cas 1 : Données insuffisantes (Edge case)
    if total_freelances < 5:
        interpretation = "Attention : L'échantillon de données est trop faible pour tirer des conclusions statistiques fiables."

    # Cas 2 : Communauté homogène et performante
    else:
        # Évaluation de la performance centrale et de la dispersion
        statut_performance = "haute" if mediane >= 70 else "modérée" if mediane >= 50 else "faible"
        statut_dispersion = "très homogène" if IQR <= 25 else "dispersée"

        interpretation = (
            f"La performance globale de la plateforme est {statut_performance} : "
            f"la moitié de vos freelances obtiennent une note supérieure à {mediane:.1f}/100. "
            f"L'intervalle interquartile (IQR) de {IQR:.1f} points indique que le cœur du réseau (50% centraux) "
            f"est {statut_dispersion} et concentré."
        )

        # Gestion dynamique des anomalies (Outliers)
        if len(cas_extremes) > 0:
            liste_ids = ", ".join(cas_extremes["id"].astype(str).tolist())
            interpretation += (
                f" L'analyse détecte {len(cas_extremes)} cas statistiquement extrême(s) "
                f"en dehors de la norme (Profils : {liste_ids}). Ces profils atypiques expliquent "
                f"pourquoi la moyenne ({moyenne:.1f}) est tirée vers le bas par rapport à la médiane."
            )
        else:
            interpretation += " Aucun profil ne s'écarte anormalement de la tendance générale."

    # --- 4. CRÉATION DES GRAPHES SÉPARÉS ---
    sns.set_theme(style="whitegrid")

    # Graphique A : Boxplot (Boîte à moustaches seule)
    fig_box, ax_box = plt.subplots(figsize=(10, 2.5))
    sns.boxplot(x=score, ax=ax_box, color="#3498db")
    ax_box.set_title("Détection visuelle des anomalies (Boxplot)", fontsize=12, fontweight="bold")
    ax_box.set_xlabel("Score")
    plt.tight_layout()

    # Graphique B : Histogramme seul
    fig_hist, ax_hist = plt.subplots(figsize=(10, 4.5))
    sns.histplot(data=df, x="score_performance", ax=ax_hist, kde=True, color="#2ecc71", bins=15)
    ax_hist.axvline(moyenne, color='red', linestyle='--', linewidth=2, label=f'Moyenne ({moyenne:.1f})')
    ax_hist.axvline(mediane, color='blue', linestyle='-', linewidth=2, label=f'Médiane ({mediane:.1f})')
    ax_hist.set_title("Distribution globale des scores", fontsize=12, fontweight="bold")
    ax_hist.set_xlabel("Score de performance (0 à 100)")
    ax_hist.set_ylabel("Nombre de freelances")
    ax_hist.legend()
    plt.tight_layout()

    return metriques, fig_box, fig_hist, interpretation