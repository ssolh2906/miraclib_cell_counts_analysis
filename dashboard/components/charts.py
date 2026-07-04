"""Charts drawn directly from outputs/*.csv in the dashboard process.

Kept separate from src/ui/plots.py (the pipeline's pre-rendered PNGs) - these
build a matplotlib Figure from an already-loaded DataFrame.
"""

import matplotlib.pyplot as plt
import pandas as pd

from src.domain.vocab import POPULATION_COLORS


def cliffs_delta_chart(response_stats: pd.DataFrame) -> plt.Figure:
    """Horizontal lollipop chart: Cliff's delta per population, annotated with p/q."""
    populations = response_stats["population"].tolist()
    y = list(range(len(populations)))
    colors = [POPULATION_COLORS.get(p, "#898781") for p in populations]

    fig, ax = plt.subplots(figsize=(5.5, 0.5 * len(populations) + 0.8))
    ax.hlines(y, 0, response_stats["cliffs_delta"], color=colors, linewidth=2)
    ax.scatter(response_stats["cliffs_delta"], y, color=colors, s=60, zorder=3)

    for yi, row in zip(y, response_stats.itertuples()):
        ax.annotate(
            f"p={row.p_value:.3f}, q={row.q_value:.3f}",
            (row.cliffs_delta, yi),
            xytext=(8 if row.cliffs_delta >= 0 else -8, 0),
            textcoords="offset points",
            va="center",
            ha="left" if row.cliffs_delta >= 0 else "right",
            fontsize=8,
            color="#4a4a45",
        )

    ax.axvline(0, color="#e1e0d9", linewidth=0.8, zorder=0)
    ax.set_yticks(y)
    ax.set_yticklabels(populations)
    ax.invert_yaxis()
    ax.margins(x=0.5)
    ax.set_xlabel("Cliff's delta (responder vs non-responder)")
    ax.set_title("Effect size by population, baseline (t=0)")
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)

    fig.tight_layout()
    return fig


def p_value_chart(response_stats: pd.DataFrame) -> plt.Figure:
    """Bar chart: raw p-value per population, with a significance line at 0.05."""
    populations = response_stats["population"].tolist()
    x = list(range(len(populations)))
    colors = [POPULATION_COLORS.get(p, "#898781") for p in populations]

    fig, ax = plt.subplots(figsize=(4.3, 3))
    ax.bar(x, response_stats["p_value"], color=colors, width=0.6)
    ax.axhline(0.05, color="#c0392b", linewidth=1.2, linestyle="--")
    ax.annotate("p = 0.05", (len(x) - 1, 0.05), xytext=(0, 4), textcoords="offset points",
                ha="right", fontsize=8, color="#c0392b")

    ax.set_xticks(x)
    ax.set_xticklabels(populations, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("p-value (Mann-Whitney U)")
    ax.set_title("Raw significance by population, baseline (t=0)")
    ax.set_ylim(0, max(1.0, response_stats["p_value"].max() * 1.1))
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    return fig


def q_value_chart(response_stats: pd.DataFrame) -> plt.Figure:
    """Bar chart: BH-adjusted q-value per population, with a significance line at 0.05."""
    populations = response_stats["population"].tolist()
    x = list(range(len(populations)))
    colors = [POPULATION_COLORS.get(p, "#898781") for p in populations]

    fig, ax = plt.subplots(figsize=(4.3, 3))
    ax.bar(x, response_stats["q_value"], color=colors, width=0.6)
    ax.axhline(0.05, color="#c0392b", linewidth=1.2, linestyle="--")
    ax.annotate("q = 0.05", (len(x) - 1, 0.05), xytext=(0, 4), textcoords="offset points",
                ha="right", fontsize=8, color="#c0392b")

    ax.set_xticks(x)
    ax.set_xticklabels(populations, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("BH-adjusted q-value")
    ax.set_title("Significance by population, baseline (t=0)")
    ax.set_ylim(0, max(1.0, response_stats["q_value"].max() * 1.1))
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    return fig
