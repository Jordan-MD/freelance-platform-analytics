import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix

def analyser_classification_q4(df, features=["score_performance", "nombre_mission"], target="profil"):
    """
    Classification supervisée par k-NN.
    Retourne les outils entraînés pour la simulation en direct dans Streamlit.
    """
    total = len(df)
    if total < 10:
        return None, None, {}, None, "Erreur : Données insuffisantes."

    # --- PHASE 1 : ÉVALUATION GLOBALE DU FICHIER ---
    X = df[features].fillna(0)
    y = df[target]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.3, random_state=42, stratify=y
    )

    k_voisins = min(3, len(X_train) - 1)
    model = KNeighborsClassifier(n_neighbors=k_voisins)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    class_labels = sorted(y.unique())
    matrice_conf = confusion_matrix(y_test, y_pred, labels=class_labels)

    # Diagnostic de viabilité automatique
    if df[features[1]].min() == 0 and df[features[1]].var() == 0:
        diagnostic = "⚠️ **NON VIABLE EN PRODUCTION** : Les nouveaux inscrits partagent tous les mêmes valeurs (0). Le modèle ne peut pas les départager géométriquement."
    else:
        diagnostic = "✅ **OPÉRATIONNEL** : Les données possèdent une variance suffisante pour discriminer les profils."

    interpretation = (
        f"**Modèle k-NN :** Réussite globale de **{accuracy * 100:.1f}%**\n"
        f"{diagnostic}\n\n"
        f"**Graphique :** La diagonale verte = succès. Le reste = erreurs de ciblage."
    )

    # Graphique : Matrice de Confusion
    sns.set_theme(style="whitegrid")
    fig_confusion, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(matrice_conf, annot=True, fmt="d", cmap="Greens",
                xticklabels=class_labels, yticklabels=class_labels, ax=ax, cbar=False)
    ax.set_title(f"Matrice de Confusion (k-NN, k={k_voisins})", fontsize=10, fontweight="bold")
    ax.set_xlabel("Profil Prédit")
    ax.set_ylabel("Profil Réel")
    plt.tight_layout()

    metriques = {"accuracy": accuracy, "k_utilise": k_voisins}


    return model, scaler, metriques, fig_confusion, interpretation