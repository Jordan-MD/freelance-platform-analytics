from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from visualization import plot_confusion_matrix

FEATURES = ["score_performance", "nombre_mission"]
TARGET = "profil"


def split_data(
    df: pd.DataFrame,
    features: list[str] = FEATURES,
    target: str = TARGET,
    test_size: float = 0.3,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Separe le dataset en un ensemble d'entrainement et un ensemble de test.

    Args:
        df: Le DataFrame contenant les donnees.
        features: Les colonnes utilisees comme variables explicatives.
        target: La colonne cible a predire.
        test_size: La proportion des donnees reservee au test.
        random_state: La graine utilisee pour la reproductibilite du decoupage.

    Returns:
        Un tuple (X_train, X_test, y_train, y_test).
    """
    x = df[features]
    y = df[target]
    return train_test_split(
        x, y, test_size=test_size, random_state=random_state, stratify=y
    )


def train_model(
    x_train: pd.DataFrame, y_train: pd.Series, random_state: int = 42
) -> DecisionTreeClassifier:
    """
    Entraine un arbre de decision pour predire la variable cible.

    Args:
        x_train: Les variables explicatives d'entrainement.
        y_train: La variable cible d'entrainement.
        random_state: La graine utilisee pour la reproductibilite.

    Returns:
        Le modele DecisionTreeClassifier entraine.
    """
    model = DecisionTreeClassifier(random_state=random_state, max_depth=4)
    model.fit(x_train, y_train)
    return model


def evaluate_model(
    model: DecisionTreeClassifier, x_test: pd.DataFrame, y_test: pd.Series
) -> dict[str, Any]:
    """
    Evalue les performances du modele entraine sur l'ensemble de test.

    Args:
        model: Le modele entraine.
        x_test: Les variables explicatives de test.
        y_test: La variable cible reelle de test.

    Returns:
        Un dictionnaire contenant accuracy, precision, recall, f1-score,
        la matrice de confusion et les predictions.
    """
    y_pred = model.predict(x_test)
    class_labels = sorted(y_test.unique())

    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(
            precision_score(y_test, y_pred, average="weighted", zero_division=0)
        ),
        "recall": float(
            recall_score(y_test, y_pred, average="weighted", zero_division=0)
        ),
        "f1_score": float(
            f1_score(y_test, y_pred, average="weighted", zero_division=0)
        ),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=class_labels),
        "class_labels": class_labels,
        "predictions": y_pred,
    }


def generate_interpretation(metrics: dict[str, Any]) -> str:
    """
    Genere une interpretation automatique, en langage clair, de la
    fiabilite du modele de classification et des risques associes
    a son utilisation.

    Args:
        metrics: Le dictionnaire produit par evaluate_model().

    Returns:
        Un texte d'interpretation destine a un lecteur non statisticien.
    """
    accuracy = metrics["accuracy"]

    if accuracy >= 0.85:
        confidence_comment = "un niveau de confiance eleve"
        risk_comment = "le risque d'erreur reste limite mais jamais nul"
    elif accuracy >= 0.65:
        confidence_comment = "un niveau de confiance modere"
        risk_comment = (
            "une part significative des predictions peut etre erronee, "
            "une validation humaine reste recommandee"
        )
    else:
        confidence_comment = "un niveau de confiance faible"
        risk_comment = (
            "le modele ne devrait pas etre utilise seul pour une decision "
            "importante sans verification complementaire"
        )

    return (
        f"Le modele atteint une exactitude (accuracy) de {accuracy * 100:.1f}%, "
        f"une precision de {metrics['precision'] * 100:.1f}% et un rappel de "
        f"{metrics['recall'] * 100:.1f}%, ce qui traduit {confidence_comment} "
        f"dans ses predictions. Sur le plan pratique, {risk_comment}."
    )


def analyze_q4(
    df: pd.DataFrame, features: list[str] = FEATURES, target: str = TARGET
) -> dict[str, Any]:
    """
    Execute l'analyse complete de la Question 4 : separation train/test,
    entrainement de l'arbre de decision, evaluation, generation de la
    matrice de confusion et interpretation.

    Args:
        df: Le DataFrame contenant les donnees.
        features: Les colonnes utilisees comme variables explicatives.
        target: La colonne cible a predire.

    Returns:
        Un dictionnaire regroupant les metriques, le chemin du graphique
        de matrice de confusion et l'interpretation textuelle.
    """
    x_train, x_test, y_train, y_test = split_data(df, features, target)
    model = train_model(x_train, y_train)
    metrics = evaluate_model(model, x_test, y_test)

    confusion_path = plot_confusion_matrix(
        matrix=metrics["confusion_matrix"],
        class_labels=[str(label) for label in metrics["class_labels"]],
    )

    interpretation = generate_interpretation(metrics)

    return {
        "accuracy": metrics["accuracy"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1_score"],
        "confusion_matrix": metrics["confusion_matrix"].tolist(),
        "confusion_matrix_path": confusion_path,
        "interpretation": interpretation,
    }
