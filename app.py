import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src import q1_univariate, q2_bivariate, q3_clustering, q4_classification
from src import utils

# ─────────────────────────────────────────────────────────
# CONFIGURATION GLOBALE
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plateforme Freelance — Analyse Statistique",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a polished look
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1e293b; margin-bottom: 0.3rem; }
    .sub-header { font-size: 1.05rem; color: #64748b; margin-bottom: 1.5rem; }
    .kpi-card { background: #ffffff; border-radius: 12px; padding: 1.2rem; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid #e2e8f0; text-align: center; }
    .kpi-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.4rem; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: #1e293b; }
    .insight-box { background: #ecfdf5; border-left: 4px solid #10b981; border-radius: 8px; 
                   padding: 1rem 1.2rem; margin-top: 1.2rem; }
    .insight-title { font-weight: 700; color: #065f46; margin-bottom: 0.4rem; font-size: 0.95rem; }
    .insight-text { color: #065f46; font-size: 0.9rem; line-height: 1.5; }
    .warning-box { background: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 8px; 
                   padding: 1rem 1.2rem; margin-top: 1.2rem; }
    .warning-title { font-weight: 700; color: #92400e; margin-bottom: 0.4rem; font-size: 0.95rem; }
    .warning-text { color: #92400e; font-size: 0.9rem; line-height: 1.5; }
    .danger-box { background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 8px; 
                  padding: 1rem 1.2rem; margin-top: 1.2rem; }
    .danger-title { font-weight: 700; color: #991b1b; margin-bottom: 0.4rem; font-size: 0.95rem; }
    .danger-text { color: #991b1b; font-size: 0.9rem; line-height: 1.5; }
    .tech-details { background: #f1f5f9; border-radius: 8px; padding: 0.8rem 1rem; 
                   margin-top: 1rem; font-size: 0.82rem; color: #475569; }
    .section-title { font-size: 1.3rem; font-weight: 600; color: #1e293b; margin: 1.5rem 0 0.8rem 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# CHARGEMENT DES DONNÉES (mise en cache)
# ─────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    """Charge le dataset CSV depuis le dossier dataset/."""
    csv_path = os.path.join(os.path.dirname(__file__), "dataset", "dataset_freelance_groupe.csv")
    if not os.path.exists(csv_path):
        st.error(f"Fichier dataset introuvable : {csv_path}")
        st.stop()
    df = pd.read_csv(csv_path)
    return df

# ─────────────────────────────────────────────────────────
# SIDEBAR — NAVIGATION
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bar-chart.png", width=48)
    st.title("Navigation")
    st.markdown("---")

    page = st.radio(
        "",
        ["🏠 Accueil", "📊 Q1 — Répartition", "🔗 Q2 — Corrélation", 
         "🎯 Q3 — Groupes naturels", "🤖 Q4 — Automatisation"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("**INF232 — Analyse de données**")
    st.caption("Thème B : Plateforme freelance")
    st.caption("80 freelances | Graine déterministe")

# ─────────────────────────────────────────────────────────
# PAGE : ACCUEIL
# ─────────────────────────────────────────────────────────
def page_accueil(df):
    st.markdown('<div class="main-header">Tableau de bord Freelance</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Plateforme de mise en relation — Vue d\'ensemble des 80 freelances</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    total = len(df)
    premium_pct = (df["profil"] == "Premium").mean() * 100
    score_mean = df["score_performance"].mean()
    corr_val = df[["score_performance", "nombre_mission"]].corr().iloc[0, 1]

    with col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Freelances inscrits</div><div class="kpi-value">{total}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Profils Premium</div><div class="kpi-value">{premium_pct:.0f}%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Score moyen</div><div class="kpi-value">{score_mean:.1f}<span style="font-size:0.9rem;color:#64748b">/100</span></div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Corrélation Missions/Score</div><div class="kpi-value">{corr_val:.2f}</div></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.markdown('<div class="section-title">Aperçu du dataset</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=280)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(label="📥 Télécharger le dataset (CSV)", data=csv, file_name="dataset_freelance_groupe.csv", mime="text/csv")
    with col_right:
        st.markdown('<div class="section-title">Répartition des profils</div>', unsafe_allow_html=True)
        profil_counts = df["profil"].value_counts()
        fig_pie, _ = utils.make_pie_chart(profil_counts)
        st.pyplot(fig_pie, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
        <div class="insight-title">💡 Résumé exécutif pour le comité d'investisseurs</div>
        <div class="insight-text">
            Sur 80 freelances analysés, la performance moyenne s\'établit à {:.1f}/100 avec une dispersion modérée. 
            La moitié des profils sont classés Premium. Une relation modérée existe entre l\'activité (missions) 
            et la performance (r = {:.2f}), ce qui ouvre la voie à une segmentation automatique partielle. 
            Les données révèlent des groupes naturels de profils et permettent de prédire le statut Premium 
            avec une fiabilité d\'environ 90%.
        </div>
    </div>
    """.format(score_mean, corr_val), unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# PAGE : Q1 — RÉPARTITION
# ─────────────────────────────────────────────────────────
def page_q1(df):
    st.markdown('<div class="main-header">Q1 — Comment se répartissent mes freelances ?</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Analyse de la performance globale et détection des cas extrêmes</div>', unsafe_allow_html=True)

    metriques, fig_box, fig_hist, interpretation = q1_univariate.analyser_performance_q1(df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Score moyen</div><div class="kpi-value">{metriques["moyenne"]:.1f}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Médiane</div><div class="kpi-value">{metriques["mediane"]:.1f}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Écart-type</div><div class="kpi-value">{metriques["ecart_type"]:.1f}</div></div>', unsafe_allow_html=True)
    with c4:
        color = "#ef4444" if metriques["nb_outliers"] > 0 else "#1e293b"
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Cas extrêmes</div><div class="kpi-value" style="color:{color};">{metriques["nb_outliers"]}</div></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.markdown('<div class="section-title">Distribution des scores</div>', unsafe_allow_html=True)
        st.pyplot(fig_hist, use_container_width=True)
    with col_right:
        st.markdown('<div class="section-title">Détection des anomalies</div>', unsafe_allow_html=True)
        st.pyplot(fig_box, use_container_width=True)

    if metriques["nb_outliers"] > 0:
        Q1 = df["score_performance"].quantile(0.25)
        Q3 = df["score_performance"].quantile(0.75)
        IQR = Q3 - Q1
        limite_basse = Q1 - 1.5 * IQR
        limite_haute = Q3 + 1.5 * IQR
        cas_extremes = df[(df["score_performance"] < limite_basse) | (df["score_performance"] > limite_haute)]
        st.markdown('<div class="section-title">📋 Profils atypiques détectés</div>', unsafe_allow_html=True)
        st.dataframe(cas_extremes[["id", "score_performance", "nombre_mission", "profil"]], use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">💡 Pour ton prochain comité d'investisseurs</div>
        <div class="insight-text">{interpretation}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔬 Détails techniques — Méthode IQR"):
        Q1 = df["score_performance"].quantile(0.25)
        Q3 = df["score_performance"].quantile(0.75)
        IQR = Q3 - Q1
        limite_basse = Q1 - 1.5 * IQR
        limite_haute = Q3 + 1.5 * IQR
        st.markdown(f"""
        **Méthode des quartiles (IQR)** :  
        - Q1 = {Q1:.2f} | Q3 = {Q3:.2f} | IQR = {IQR:.2f}  
        - Limites : [{limite_basse:.2f} ; {limite_haute:.2f}]  
        Un freelance est considéré comme extrême si son score est en dehors de cet intervalle.
        """)

# ─────────────────────────────────────────────────────────
# PAGE : Q2 — CORRÉLATION
# ─────────────────────────────────────────────────────────
def page_q2(df):
    st.markdown('<div class="main-header">Q2 — Le nombre de missions prédit-il la performance ?</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Corrélation de Pearson, régression linéaire et limites de l\'anticipation</div>', unsafe_allow_html=True)

    metriques, fig_scatter, scenarios = q2_bivariate.analyser_relations_q2(df)

    r = metriques["r_activite"]
    p = metriques["p_activite"]
    r2 = metriques["r_squared"]
    erreur = metriques["erreur_type"]
    pente = metriques["pente"]
    intercept = metriques["intercept"]
    x_min = metriques["x_min"]
    x_max = metriques["x_max"]
    x_mediane = metriques["x_mediane_missions"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Corrélation (r)</div><div class="kpi-value" style="color:#3b82f6;">{r:.2f}</div></div>', unsafe_allow_html=True)
    with c2:
        sig_color = "#10b981" if p < 0.05 else "#ef4444"
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">p-value</div><div class="kpi-value" style="color:{sig_color};">{p:.2e}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">R² (variance expliquée)</div><div class="kpi-value">{r2*100:.1f}%</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Erreur type</div><div class="kpi-value">±{erreur:.1f} pts</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Nuage de points : Missions vs Performance</div>', unsafe_allow_html=True)
    st.pyplot(fig_scatter, use_container_width=True)

    st.markdown('<div class="section-title">📋 Diagnostic de la relation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="insight-box" style="background:#eff6ff;border-color:#bfdbfe;">
        <div class="insight-text" style="color:#1e40af;">{scenarios.get("statut_lien", "")}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🧮 Scénarios concrets d\'anticipation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="warning-box">
        <div class="warning-text">{scenarios.get("predictions_cas", "")}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🎛️ Simulateur interactif</div>', unsafe_allow_html=True)
    col_sim, col_res = st.columns([2, 3])
    with col_sim:
        x_min_int, x_max_int = int(x_min), int(x_max)
        missions_input = st.slider("Nombre de missions du nouveau freelance", 0, x_max_int + 20, x_mediane)
        score_pred = pente * missions_input + intercept
        score_pred = max(0, min(100, score_pred))
        st.markdown(f"""
        <div style="background:#f8fafc;border-radius:10px;padding:1rem;border:1px solid #e2e8f0;text-align:center;margin-top:0.5rem;">
            <div style="font-size:0.8rem;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">Score estimé</div>
            <div style="font-size:2rem;font-weight:700;color:#1e293b;">{score_pred:.1f}<span style="font-size:1rem;color:#64748b">/100</span></div>
            <div style="font-size:0.8rem;color:#64748b;margin-top:0.3rem;">±{erreur:.1f} pts de marge</div>
        </div>
        """, unsafe_allow_html=True)

    with col_res:
        if missions_input < x_min_int:
            zone_class, zone_title, zone_text = "danger-box", "🔴 Extrapolation risquée", f"Aucun freelance dans vos données n\'a moins de {x_min_int} missions. Cette prédiction sort du domaine connu."
        elif missions_input > x_max_int:
            zone_class, zone_title, zone_text = "danger-box", "🔴 Extrapolation risquée", f"Aucun freelance dans vos données n\'a plus de {x_max_int} missions. Le modèle n\'a jamais vu ce niveau d\'activité."
        elif abs(missions_input - x_mediane) <= 5:
            zone_class, zone_title, zone_text = "insight-box", "🟢 Zone de confiance maximale", f"Ce niveau d\'activité ({missions_input}) est proche de la médiane ({x_mediane}). La prédiction est ici la plus fiable."
        else:
            zone_class, zone_title, zone_text = "warning-box", "🟡 Zone valide", "Le freelance est dans la plage observée, mais éloigné du centre des données. Comptez une marge d\'erreur plus large."
        st.markdown(f"""
        <div class="{zone_class}">
            <div class="{zone_class.replace('-box', '-title')}">{zone_title}</div>
            <div class="{zone_class.replace('-box', '-text')}">{zone_text}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-title">💡 Verdict</div>
        <div class="insight-text">
            Le lien entre missions et performance est <strong>{"significatif et modéré" if p < 0.05 and abs(r) >= 0.4 else "faible ou non significatif"}</strong> (r = {r:.2f}, p {'< 0.05' if p < 0.05 else '>= 0.05'}). 
            On peut utiliser le nombre de missions comme <strong>indicateur d\'alerte</strong>, mais pas comme prédicteur suffisant à lui seul. 
            D\'autres facteurs comptent pour <strong>{(1-r2)*100:.0f}%</strong> de la performance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔬 Détails techniques — Régression linéaire"):
        st.markdown(f"""
        **Équation** : Score = {pente:.3f} × Missions + {intercept:.3f}  
        **R²** : {r2:.3f} | **Erreur type** : {erreur:.2f}  
        **Plage observée** : [{int(x_min)} ; {int(x_max)}] missions | **Médiane** : {x_mediane}
        """)

# ─────────────────────────────────────────────────────────
# PAGE : Q3 — CLUSTERING
# ─────────────────────────────────────────────────────────
def page_q3(df):
    st.markdown('<div class="main-header">Q3 — Quels groupes naturels se dessinent ?</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Classification non supervisée — K-Means avec justification du nombre de clusters</div>', unsafe_allow_html=True)

    metriques, fig_selection, fig_clusters, interpretation = q3_clustering.analyser_profils_q3(df)

    if not metriques:
        st.error(interpretation)
        return

    meilleur_k = metriques["meilleur_k"]
    silhouette_max = metriques["silhouette_max"]
    ref_score = metriques["ref_score"]
    ref_missions = metriques["ref_missions"]
    effectifs = metriques["effectifs"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Groupes trouvés</div><div class="kpi-value">{meilleur_k}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Score Silhouette</div><div class="kpi-value">{silhouette_max:.2f}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Méthode de choix</div><div class="kpi-value" style="font-size:1.2rem;">Coude + Silhouette</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Justification du nombre de groupes</div>', unsafe_allow_html=True)
    st.pyplot(fig_selection, use_container_width=True)

    st.markdown('<div class="section-title">Cartographie des groupes naturels</div>', unsafe_allow_html=True)
    st.pyplot(fig_clusters, use_container_width=True)

    st.markdown('<div class="section-title">📋 Description des profils identifiés</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="insight-box">
        <div class="insight-text">{interpretation}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 Répartition des effectifs</div>', unsafe_allow_html=True)
    effectif_data = []
    for cid, count in sorted(effectifs.items()):
        pct = count / len(df) * 100
        effectif_data.append({"Groupe": f"Groupe {cid + 1}", "Freelances": count, "% du total": f"{pct:.1f}%"})
    st.table(pd.DataFrame(effectif_data))

    st.markdown(f"""
    <div class="warning-box">
        <div class="warning-title">📌 Points de référence de la plateforme</div>
        <div class="warning-text">
            <strong>Score moyen global :</strong> {ref_score:.1f}/100 | 
            <strong>Activité moyenne globale :</strong> {ref_missions:.1f} missions
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔬 Détails techniques — K-Means"):
        st.markdown(f"""
        **Algorithme** : K-Means (scikit-learn) | **Normalisation** : StandardScaler  
        **Variables** : score_performance, nombre_mission  
        **K retenu** : {meilleur_k} (sélection automatique par silhouette maximal)  
        **Score silhouette** : {silhouette_max:.3f} | **Plage K testée** : 2 à {min(6, len(df)-1)}
        """)

# ─────────────────────────────────────────────────────────
# PAGE : Q4 — CLASSIFICATION
# ─────────────────────────────────────────────────────────
def page_q4(df):
    st.markdown('<div class="main-header">Q4 — Puis-je automatiser Premium vs Standard ?</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Classification supervisée — k-NN et évaluation du risque commercial</div>', unsafe_allow_html=True)

    model, scaler, metriques, fig_confusion, interpretation = q4_classification.analyser_classification_q4(df)

    if model is None:
        st.error(interpretation)
        return

    acc = metriques["accuracy"]
    k_utilise = metriques["k_utilise"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Exactitude (Accuracy)</div><div class="kpi-value" style="color:#3b82f6;">{acc*100:.1f}%</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Algorithme</div><div class="kpi-value" style="font-size:1.3rem;">k-NN</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-label">Voisins (k)</div><div class="kpi-value">{k_utilise}</div></div>', unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-title">Matrice de confusion</div>', unsafe_allow_html=True)
        st.pyplot(fig_confusion, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">🎛️ Simulateur d\'orientation</div>', unsafe_allow_html=True)

        score_input = st.slider("Score de performance", 0.0, 100.0, 70.0, 0.5)
        missions_input = st.slider("Nombre de missions", 0, 150, 45)

        # k-NN prediction with scaler
        input_data = np.array([[score_input, missions_input]])
        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)
        proba = model.predict_proba(input_scaled)

        pred_label = prediction[0]
        pred_proba = max(proba[0]) * 100

        badge_bg = "#d1fae5" if pred_label == "Premium" else "#fee2e2"
        badge_color = "#065f46" if pred_label == "Premium" else "#991b1b"

        st.markdown(f"""
        <div style="background:#f8fafc;border-radius:10px;padding:1.2rem;border:1px solid #e2e8f0;text-align:center;margin-top:0.5rem;">
            <div style="font-size:0.8rem;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:0.5rem;">Orientation prédite</div>
            <div style="display:inline-block;padding:8px 20px;border-radius:20px;font-weight:700;font-size:1.1rem;background:{badge_bg};color:{badge_color};">
                {pred_label} — {pred_proba:.0f}% confiance
            </div>
            <div style="font-size:0.75rem;color:#64748b;margin-top:0.6rem;">
                Score : {score_input:.1f} | Missions : {missions_input}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📋 Diagnostic du modèle</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="insight-box" style="background:#eff6ff;border-color:#bfdbfe;">
        <div class="insight-text" style="color:#1e40af;">{interpretation}</div>
    </div>
    """, unsafe_allow_html=True)

    erreur_rate = (1 - acc) * 100
    st.markdown(f"""
    <div class="danger-box">
        <div class="danger-title">⚠️ Risque commercial si confiance aveugle</div>
        <div class="danger-text">
            Avec une exactitude de <strong>{acc*100:.1f}%</strong>, environ <strong>{erreur_rate:.1f}%</strong> des nouveaux freelances 
            seront mal orientés. Sur 100 inscriptions, cela représente ~<strong>{round(erreur_rate)} erreurs</strong>.  
            <br><br>
            <strong>Recommandation</strong> : utiliser le modèle comme <strong>tri préliminaire</strong>, 
            mais garder une validation humaine pour les cas limites.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔬 Détails techniques — k-NN"):
        st.markdown(f"""
        **Modèle** : KNeighborsClassifier (k={k_utilise})  
        **Split** : 70% entraînement / 30% test (stratifié)  
        **Normalisation** : StandardScaler appliquée avant prédiction  
        **Variables** : score_performance, nombre_mission  
        **Cible** : profil (Premium / Standard)  
        **Exactitude** : {acc:.3f}
        """)

# ─────────────────────────────────────────────────────────
# ROUTER PRINCIPAL
# ─────────────────────────────────────────────────────────
def main():
    df = load_data()

    if page == "🏠 Accueil":
        page_accueil(df)
    elif page == "📊 Q1 — Répartition":
        page_q1(df)
    elif page == "🔗 Q2 — Corrélation":
        page_q2(df)
    elif page == "🎯 Q3 — Groupes naturels":
        page_q3(df)
    elif page == "🤖 Q4 — Automatisation":
        page_q4(df)

if __name__ == "__main__":
    main()