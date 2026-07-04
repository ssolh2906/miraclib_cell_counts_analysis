"""
Part 3 figures: responder vs non-responder, per population.
Prototyped and eyeballed in notebooks/part3_stats.ipynb before landing here.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve

from src.domain.vocab import POPULATION_COLORS, POPULATION_COLUMNS

OUTPUTS_DIR = Path(__file__).resolve().parents[2] / "outputs"

COLOR_RESPONDER = "#2a78d6"
COLOR_NON_RESPONDER = "#1baf7a"


def save_boxplots(freq_with_response: pd.DataFrame, path: Path = OUTPUTS_DIR / "boxplots.png") -> None:
    """Grouped boxplot + jitter, responder vs non-responder, one group per population."""
    fig, ax = plt.subplots(figsize=(9, 5))

    for i, population in enumerate(POPULATION_COLUMNS):
        resp = freq_with_response.loc[
            (freq_with_response.population == population) & (freq_with_response.response == "yes"), "percentage"
        ]
        non = freq_with_response.loc[
            (freq_with_response.population == population) & (freq_with_response.response == "no"), "percentage"
        ]

        bp = ax.boxplot([resp, non], positions=[i - 0.18, i + 0.18], widths=0.32,
                         patch_artist=True, showfliers=False)
        for patch, color in zip(bp["boxes"], [COLOR_RESPONDER, COLOR_NON_RESPONDER]):
            patch.set_facecolor(color)
            patch.set_alpha(0.35)
        for median in bp["medians"]:
            median.set_color("#0b0b0b")

        rng = np.random.default_rng(0)
        ax.scatter(rng.normal(i - 0.18, 0.03, len(resp)), resp, color=COLOR_RESPONDER, s=10, alpha=0.6)
        ax.scatter(rng.normal(i + 0.18, 0.03, len(non)), non, color=COLOR_NON_RESPONDER, s=10, alpha=0.6)

    ax.set_xticks(range(len(POPULATION_COLUMNS)))
    ax.set_xticklabels(POPULATION_COLUMNS)
    ax.set_ylabel("relative frequency (%)")
    ax.set_title("Population frequency: responder vs non-responder (baseline, t=0)")
    ax.grid(axis="y", color="#e1e0d9", linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=COLOR_RESPONDER, alpha=0.35),
               plt.Rectangle((0, 0), 1, 1, facecolor=COLOR_NON_RESPONDER, alpha=0.35)]
    ax.legend(handles, ["responder", "non-responder"], frameon=False)

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_melanoma_miraclib_pbmc_baseline_boxplots_by_sex(
    baseline_response_frequencies: pd.DataFrame,
    path: Path = OUTPUTS_DIR / "melanoma_miraclib_pbmc_baseline_boxplots_by_sex.png",
) -> None:
    """Same grouped boxplot + jitter as Part 3, faceted into one panel per sex (M, F)."""
    sexes = ["M", "F"]
    fig, axes = plt.subplots(1, len(sexes), figsize=(15, 5), sharey=True)

    for ax, sex in zip(axes, sexes):
        sex_freq = baseline_response_frequencies.loc[baseline_response_frequencies["sex"] == sex]

        for i, population in enumerate(POPULATION_COLUMNS):
            resp = sex_freq.loc[
                (sex_freq.population == population) & (sex_freq.response == "yes"), "percentage"
            ]
            non = sex_freq.loc[
                (sex_freq.population == population) & (sex_freq.response == "no"), "percentage"
            ]

            bp = ax.boxplot([resp, non], positions=[i - 0.18, i + 0.18], widths=0.32,
                             patch_artist=True, showfliers=False)
            for patch, color in zip(bp["boxes"], [COLOR_RESPONDER, COLOR_NON_RESPONDER]):
                patch.set_facecolor(color)
                patch.set_alpha(0.35)
            for median in bp["medians"]:
                median.set_color("#0b0b0b")

            rng = np.random.default_rng(0)
            ax.scatter(rng.normal(i - 0.18, 0.03, len(resp)), resp, color=COLOR_RESPONDER, s=10, alpha=0.6)
            ax.scatter(rng.normal(i + 0.18, 0.03, len(non)), non, color=COLOR_NON_RESPONDER, s=10, alpha=0.6)

        ax.set_xticks(range(len(POPULATION_COLUMNS)))
        ax.set_xticklabels(POPULATION_COLUMNS)
        ax.set_title(f"sex = {sex}")
        ax.grid(axis="y", color="#e1e0d9", linewidth=0.8)
        ax.set_axisbelow(True)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)

    axes[0].set_ylabel("relative frequency (%)")
    fig.suptitle("Population frequency by sex: responder vs non-responder (baseline, t=0)")

    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=COLOR_RESPONDER, alpha=0.35),
               plt.Rectangle((0, 0), 1, 1, facecolor=COLOR_NON_RESPONDER, alpha=0.35)]
    axes[-1].legend(handles, ["responder", "non-responder"], frameon=False)

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_pca_scatter(pca: pd.DataFrame, path: Path = OUTPUTS_DIR / "pca.png") -> None:
    """2D PCA scatter of each sample's population profile, responder vs non-responder,
    with each group's centroid marked (X) to make the (modest) separation explicit."""
    fig, ax = plt.subplots(figsize=(6, 6))

    for response, color, label in [("yes", COLOR_RESPONDER, "responder"), ("no", COLOR_NON_RESPONDER, "non-responder")]:
        group = pca.loc[pca["response"] == response]
        ax.scatter(group["pc1"], group["pc2"], color=color, s=14, alpha=0.5, label=label)
        ax.scatter(group["pc1"].mean(), group["pc2"].mean(), color=color, s=90, marker="X",
                   edgecolor="#0b0b0b", linewidth=0.8, zorder=5)

    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("PCA of population profile: responder vs non-responder (baseline, t=0)")
    ax.legend(frameon=False)
    ax.axhline(0, color="#e1e0d9", linewidth=0.8, zorder=0)
    ax.axvline(0, color="#e1e0d9", linewidth=0.8, zorder=0)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def save_roc_curves(
    freq_with_response: pd.DataFrame,
    auc_table: pd.DataFrame,
    path: Path = OUTPUTS_DIR / "roc_curves.png",
) -> None:
    """ROC curve per population, responder ('yes') as the positive class."""
    fig, ax = plt.subplots(figsize=(6, 6))

    for population in POPULATION_COLUMNS:
        group = freq_with_response.loc[freq_with_response["population"] == population]
        y_true = (group["response"] == "yes").astype(int)
        fpr, tpr, _ = roc_curve(y_true, group["percentage"])
        auc = auc_table.loc[auc_table["population"] == population, "auc"].iloc[0]
        ax.plot(fpr, tpr, color=POPULATION_COLORS[population], linewidth=1.2,
                label=f"{population} (AUC={auc:.2f})")

    ax.plot([0, 1], [0, 1], color="#898781", linewidth=1, linestyle="--")  # chance line
    ax.set_xlabel("false positive rate")
    ax.set_ylabel("true positive rate")
    ax.set_title("ROC curves per population (baseline, t=0)")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)