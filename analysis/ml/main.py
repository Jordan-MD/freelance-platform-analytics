from eda import print_eda_report, run_eda
from loader import load_dataset
from q1_statistics import analyze_q1
from q2_correlation import analyze_q2
from q3_clustering import analyze_q3
from q4_classification import analyze_q4
from utils import export_results_json, print_section

# Adaptez ce chemin vers l'emplacement de votre dataset genere (Phase 1)
DATA_PATH = "../dataset/dataset_freelance_groupe.csv"


def main() -> None:
    """
    Execute l'ensemble du pipeline d'analyse : chargement, EDA, puis
    traitement sequentiel des quatre questions du TP, avec export
    des resultats au format JSON et des graphiques dans figures/.
    """
    df = load_dataset(DATA_PATH)

    print_section("EXPLORATION DES DONNEES (EDA)")
    eda_results = run_eda(df)
    print_eda_report(eda_results)

    print_section("QUESTION 1 - Statistique univariee")
    q1_results = analyze_q1(df)
    print(q1_results["interpretation"])

    print_section("QUESTION 2 - Correlation et regression")
    q2_results = analyze_q2(df)
    print(q2_results["interpretation"])

    print_section("QUESTION 3 - Classification non supervisee (K-Means)")
    q3_results = analyze_q3(df)
    print(q3_results["interpretation"])

    print_section("QUESTION 4 - Classification supervisee (Decision Tree)")
    q4_results = analyze_q4(df)
    print(q4_results["interpretation"])

    export_results_json(
        {
            "q1": q1_results,
            "q2": q2_results,
            "q3": q3_results,
            "q4": q4_results,
        },
        output_path="results/analysis_results.json",
    )
    print_section(
        "Analyse terminee - resultats exportes dans results/analysis_results.json "
        "et graphiques dans figures/"
    )


if __name__ == "__main__":
    main()
