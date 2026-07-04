import streamlit as st

from components.data_loading import (
    load_cell_frequencies,
    load_cohort_counts,
    load_population_means,
)


def _cohort_value(cohort, metric, group):
    row = cohort[(cohort["metric"] == metric) & (cohort["group"] == group)]
    return int(row["value"].iloc[0]) if not row.empty else 0


def render() -> None:
    st.header("Overview")
    st.markdown(
        "Analysis of PBMC immune-cell populations from **cell-count.csv** to understand how the "
        "drug candidate **miraclib** relates to treatment response in melanoma patients."
    )

    freq = load_cell_frequencies()
    cohort = load_cohort_counts()

    n_samples = freq["sample"].nunique()
    n_responder = _cohort_value(cohort, "subjects_per_response", "yes")
    n_non_responder = _cohort_value(cohort, "subjects_per_response", "no")
    n_baseline = n_responder + n_non_responder

    means = load_population_means()
    b_cell_headline = means.loc[
        (means["sex"] == "M") & (means["response"] == "yes") & (means["population"] == "b_cell"),
        "mean_cell_count",
    ].iloc[0]

    st.subheader("At a glance")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total samples", f"{n_samples:,}")
    c2.metric("Baseline cohort (subjects)", f"{n_baseline:,}")
    c3.metric("Responders / Non-responders", f"{n_responder} / {n_non_responder}")
    c4.metric("Mean B cells — mel. male responders", f"{b_cell_headline:,.2f}")
    st.caption(
        "Baseline cohort = melanoma + miraclib + PBMC at treatment start (t=0). "
        "Chosen to avoid pseudoreplication and to frame response as a predictive "
        "biomarker (the individual's baseline **immune setpoint**)."
    )

    st.divider()

    st.subheader("What's in this dashboard")
    st.markdown(
        "- **🧬 Part 2 · Frequencies** — relative frequency of each cell population per sample.\n"
        "- **📈 Part 3 · Stats** — responder vs non-responder comparison at baseline "
        "(Mann-Whitney U, Cliff's delta effect size, BH-corrected q-values) with boxplots, PCA, and ROC.\n"
        "- **🔬 Part 4 · Subset** — melanoma + miraclib + PBMC baseline subset, cohort composition, "
        "and per-population means."
    )
    st.caption("Use the sidebar to navigate. All views read pre-computed tables from `outputs/`.")
