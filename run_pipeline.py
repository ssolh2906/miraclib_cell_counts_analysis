"""
Run with `python run_pipeline.py` from repo root.
Reads cell_counts.db and writes outputs/*.csv, outputs/*.png.
"""

import sqlite3
from pathlib import Path

from src.data.repository import (
    get_annotated_cell_counts,
    get_baseline_miraclib_melanoma_pbmc_samples,
    get_melanoma_miraclib_pbmc_baseline_samples_per_project,
    get_melanoma_miraclib_pbmc_baseline_subjects_per_response,
    get_melanoma_miraclib_pbmc_baseline_subjects_per_sex,
)
from src.domain.frequency import compute_frequencies_with_metadata
from src.domain.statistics import (
    compare_responders,
    compute_response_frequencies,
    filter_predictive_subset,
    pca_projection,
    population_auc,
)
from src.domain.subsets import combine_cohort_counts, filter_melanoma_miraclib_pbmc_baseline, summarize_population_means
from src.ui.plots import save_boxplots, save_pca_scatter, save_roc_curves
from src.ui.tables import (
    save_cell_frequencies,
    save_cohort_counts,
    save_melanoma_miraclib_pbmc_baseline_samples,
    save_population_means,
    save_response_stats,
)

DB_PATH = Path(__file__).resolve().parent / "cell_counts.db"


def generate_frequency_summary(conn: sqlite3.Connection) -> None:
    """Part 2: frequency summary table, one row per (sample, population).

    Uses annotated counts (with subject/sample metadata) so the exported table
    carries cohort columns the dashboard filters on.
    """
    annotated = get_annotated_cell_counts(conn)
    frequencies = compute_frequencies_with_metadata(annotated)
    save_cell_frequencies(frequencies)


def analyze_responder_differences(conn: sqlite3.Connection) -> None:
    """Part 3: responder vs non-responder comparison: stats table, boxplots, ROC curves, PCA scatter."""
    annotated_counts = get_annotated_cell_counts(conn)
    subset = filter_predictive_subset(annotated_counts)
    freq_with_response = compute_response_frequencies(subset)

    stats = compare_responders(freq_with_response)
    auc_table = population_auc(freq_with_response)
    pca = pca_projection(freq_with_response)

    save_response_stats(stats)
    save_boxplots(freq_with_response)
    save_roc_curves(freq_with_response, auc_table)
    save_pca_scatter(pca)


def analyze_melanoma_miraclib_pbmc_baseline(conn: sqlite3.Connection) -> None:
    """Part 4: melanoma + miraclib + PBMC baseline subset - identify, counts, population means."""
    save_melanoma_miraclib_pbmc_baseline_samples(get_baseline_miraclib_melanoma_pbmc_samples(conn))

    counts = combine_cohort_counts(
        get_melanoma_miraclib_pbmc_baseline_samples_per_project(conn),
        get_melanoma_miraclib_pbmc_baseline_subjects_per_response(conn),
        get_melanoma_miraclib_pbmc_baseline_subjects_per_sex(conn),
    )
    save_cohort_counts(counts)

    annotated_counts = get_annotated_cell_counts(conn)
    subset = filter_melanoma_miraclib_pbmc_baseline(annotated_counts)
    save_population_means(summarize_population_means(subset))


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    try:
        generate_frequency_summary(conn)
        analyze_responder_differences(conn)
        analyze_melanoma_miraclib_pbmc_baseline(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()