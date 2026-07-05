import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score

def analyser_classification_q4(df, features=["score_performance", "nombre_mission"], target="profil"):
    """
    Classification supervisée par k-NN.
    Retourne les outils entraînés pour la simulation en direct dans Streamlit.
    """
    total = len(df)
    if total < 10:
        return None, None, {}, None, "Erreur : Données insuffisantes."

    # --- PHASE 1 : ÉVALUATION GLOBALE DU FICHIER ---
    X = df[features].fillna(df[features].median())
    y = df[target]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.3, random_state=42, stratify=y
    )

    # Optimisation de k par cross-validation (1-15)
    k_range = range(1, min(16, len(X_train)))
    cv_scores = {}
    for k in k_range:
        knn = KNeighborsClassifier(n_neighbors=k)
        scores = cross_val_score(knn, X_train, y_train, cv=5, scoring="accuracy")
        cv_scores[k] = scores.mean()

    k_optimal = max(cv_scores, key=cv_scores.get)

    model = KNeighborsClassifier(n_neighbors=k_optimal)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    class_labels = sorted(y.unique())
    matrice_conf = confusion_matrix(y_test, y_pred, labels=class_labels)

    report = classification_report(y_test, y_pred, output_dict=True)
    precision_macro = report["macro avg"]["precision"]
    recall_macro = report["macro avg"]["recall"]
    f1_macro = report["macro avg"]["f1-score"]

    interpretation = (
        f"**Modèle k-NN :** Réussite globale de **{accuracy * 100:.1f}%** (k={k_optimal}, optimisé par CV 5-fold)\n"
        f"**Précision :** {precision_macro*100:.1f}% | **Rappel :** {recall_macro*100:.1f}% | **F1-score :** {f1_macro*100:.1f}%\n\n"
        f"**Graphique :** La diagonale verte = succès. Le reste = erreurs de ciblage."
    )

    # Graphique : Matrice de Confusion
    sns.set_theme(style="whitegrid")
    fig_confusion, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(matrice_conf, annot=True, fmt="d", cmap="Greens",
                xticklabels=class_labels, yticklabels=class_labels, ax=ax, cbar=False)
    ax.set_title(f"Matrice de Confusion (k-NN, k={k_optimal})", fontsize=10, fontweight="bold")
    ax.set_xlabel("Profil Prédit")
    ax.set_ylabel("Profil Réel")
    plt.tight_layout()

    # Graphique : Accuracy vs k
    fig_k, ax_k = plt.subplots(figsize=(8, 3.5))
    ks = sorted(cv_scores.keys())
    vals = [cv_scores[k] for k in ks]
    ax_k.plot(ks, vals, "o-", color="#3b82f6", linewidth=2)
    ax_k.axvline(k_optimal, color="red", linestyle="--", label=f"k optimal = {k_optimal}")
    ax_k.set_title("Accuracy vs nombre de voisins (k)", fontsize=10, fontweight="bold")
    ax_k.set_xlabel("k (nombre de voisins)")
    ax_k.set_ylabel("Accuracy (CV 5-fold)")
    ax_k.legend()
    plt.tight_layout()

    metriques = {
        "accuracy": accuracy,
        "k_utilise": k_optimal,
        "precision": precision_macro,
        "recall": recall_macro,
        "f1": f1_macro,
    }

    return model, scaler, metriques, fig_confusion, fig_k, interpretation