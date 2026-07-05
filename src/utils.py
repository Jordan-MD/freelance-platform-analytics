import matplotlib.pyplot as plt

def make_pie_chart(profil_counts):
    """Crée un camembert de répartition des profils."""
    fig, ax = plt.subplots(figsize=(5, 5))
    colors = ["#10b981", "#ef4444"]
    wedges, texts, autotexts = ax.pie(
        profil_counts.values,
        labels=profil_counts.index,
        autopct="%1.0f%%",
        startangle=90,
        colors=colors,
        explode=(0.02, 0.02),
        shadow=False,
    )
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight("bold")
    ax.set_title("Répartition Premium / Standard", fontsize=12, fontweight="bold", pad=15)
    plt.tight_layout()
    return fig, ax