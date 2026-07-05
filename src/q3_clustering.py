import numpy as np # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
from sklearn.cluster import KMeans # type: ignore
from sklearn.metrics import silhouette_score # type: ignore
from sklearn.preprocessing import StandardScaler # type: ignore

def analyser_profils_q3(df, features=["score_performance", "nombre_mission"]):
    """
    Logique statistique de la Question 3 : Clustering Non Supervisé.
    Trouve dynamiquement le meilleur K, applique KMeans et génère des descriptions
    quantitatives comparées aux moyennes globales de la plateforme.
    """
    total = len(df)

    # Sécurité si le dataset contient trop peu de lignes pour du clustering
    if total < 10:
        return {}, None, None, "Erreur : Le volume de données est trop faible pour structurer des groupes homogènes."

    # --- 1. NETTOYAGE & NORMALISATION ---
    # Le clustering requiert des données sans valeurs manquantes
    X = df[features].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # --- 2. SÉLECTION DYNAMIQUE DU NOMBRE DE CLUSTERS (K) ---
    # On teste les configurations de 2 jusqu'à un maximum raisonnable (6 ou total-1)
    max_k = min(6, total - 1)
    k_values = range(2, max_k + 1)

    inerties = []
    silhouette_scores = {}

    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X_scaled)
        inerties.append(kmeans.inertia_)
        silhouette_scores[k] = silhouette_score(X_scaled, kmeans.labels_)

    # Sélection automatique du K ayant le score de silhouette le plus élevé
    meilleur_k = max(silhouette_scores, key=silhouette_scores.get) # type: ignore

    # --- 3. K-MEANS FINAL ---
    kmeans_final = KMeans(n_clusters=meilleur_k, random_state=42, n_init=10)
    labels = kmeans_final.fit_predict(X_scaled)

    # Conversion des centres des clusters vers l'échelle d'origine des données
    centres_originaux = scaler.inverse_transform(kmeans_final.cluster_centers_)

    # Rapprochement des résultats avec les données initiales
    df_result = df.loc[X.index].copy()
    df_result["cluster"] = labels

    # --- 4. MOTEUR DE DESCRIPTION QUANTITATIF ---
    # Calcul des pivots globaux de la plateforme pour la comparaison
    ref_score = df[features[0]].mean()
    ref_missions = df[features[1]].mean()

    interpretation = (
        f"L'analyse mathématique révèle **{meilleur_k} groupes naturels** de freelances "
        f"(Score de silhouette optimal : {silhouette_scores[meilleur_k]:.2f}).\n\n"
        f"Pour donner du sens à ces segments sans utiliser d'étiquettes arbitraires, chaque groupe est évalué "
        f"par rapport aux moyennes de la plateforme (**Note moyenne globale : {ref_score:.1f}/100** | **Activité moyenne : {ref_missions:.1f} missions**) :\n\n"
    )

    for cluster_id, group in df_result.groupby("cluster"):
        part = (len(group) / total) * 100
        m_score = group[features[0]].mean()
        m_miss = group[features[1]].mean()

        # Positionnement mathématique
        pos_score = "supérieure" if m_score >= ref_score else "inférieure"
        pos_miss = "très actif" if m_miss >= ref_missions else "faiblement actif"

        interpretation += (
            f"**Groupe {cluster_id + 1} ({len(group)} freelances, soit {part:.1f}%) :**\n"
            f"* **Performance :** {m_score:.1f}/100 (Qualité {pos_score} à la moyenne globale).\n"
            f"* **Volume d'activité :** {m_miss:.1f} missions (Comportement {pos_miss} par rapport au réseau).\n\n"
        )

    # --- 5. GRAPHES SÉPARÉS POUR STREAMLIT ---
    sns.set_theme(style="whitegrid")

    # Graphe 1 : Métriques de sélection (Coude & Silhouette)
    fig_selection, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))

    ax1.plot(k_values, inerties, 'o-', color='#34495e', linewidth=2)
    ax1.set_title("Méthode du Coude (Inertie)", fontsize=10, fontweight="bold")
    ax1.set_xlabel("Nombre de clusters (K)")
    ax1.set_ylabel("Inertie Intra-classe")

    ax2.bar(silhouette_scores.keys(), silhouette_scores.values(), color='#9b59b6', alpha=0.8)
    ax2.axhline(silhouette_scores[meilleur_k], color='red', linestyle='--', label=f"Max ({meilleur_k})")
    ax2.set_title("Validation par Silhouette", fontsize=10, fontweight="bold")
    ax2.set_xlabel("Nombre de clusters (K)")
    ax2.set_ylabel("Score moyen")
    ax2.legend()
    plt.tight_layout()

    # Graphe 2 : Cartographie des groupes réels
    fig_clusters, ax = plt.subplots(figsize=(10, 5.5))
    sns.scatterplot(data=df_result, x=features[0], y=features[1], hue="cluster", 
                    palette="tab10", s=80, alpha=0.8, ax=ax)

    # Ajout des centres géométriques (Profils types)
    ax.scatter(centres_originaux[:, 0], centres_originaux[:, 1], color='black', 
               marker='X', s=200, label="Centre de gravité (Profil type)") # type: ignore

    ax.set_title(f"Structure naturelle du réseau en {meilleur_k} sous-groupes", fontsize=11, fontweight="bold")
    ax.set_xlabel("Score de performance (0 à 100)")
    ax.set_ylabel("Nombre de missions réalisées")
    ax.legend(title="Légende")
    plt.tight_layout()

    # Variables de suivi pour l'interface
    metriques = {
        "meilleur_k": meilleur_k,
        "silhouette_max": silhouette_scores[meilleur_k],
        "ref_score": ref_score,
        "ref_missions": ref_missions,
        "effectifs": df_result["cluster"].value_counts().to_dict()
    }

    return metriques, fig_selection, fig_clusters, interpretation