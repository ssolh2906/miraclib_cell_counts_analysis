import streamlit as st

from components.data_loading import load_cell_frequencies

POPULATION_ORDER = ["b_cell", "cd4_t_cell", "cd8_t_cell", "nk_cell", "monocyte"]


def _multiselect(container, label, series, key):
    """Multiselect that treats an empty selection as 'all' (avoids an empty view)."""
    options = sorted(series.dropna().unique().tolist())
    picked = container.multiselect(label, options, default=options, key=key)
    return picked if picked else options


def render() -> None:
    st.header("Cell frequencies · Part 2")
    st.caption(
        "Relative frequency (%) of each immune-cell population per sample "
        "(count / sample total × 100). The full dataset is shown; use the filters "
        "to narrow to a cohort."
    )

    df = load_cell_frequencies()
    df["response"] = df["response"].fillna("n/a")

    st.subheader("Filters")
    r1 = st.columns(4)
    condition = _multiselect(r1[0], "Condition", df["condition"], "f_condition")
    sample_type = _multiselect(r1[1], "Sample type", df["sample_type"], "f_sampletype")
    treatment = _multiselect(r1[2], "Treatment", df["treatment"], "f_treatment")
    response = _multiselect(r1[3], "Response", df["response"], "f_response")

    r2 = st.columns(4)
    sex = _multiselect(r2[0], "Sex", df["sex"], "f_sex")
    timepoint = _multiselect(r2[1], "Timepoint (days)", df["time_from_treatment_start"], "f_time")
    population = _multiselect(r2[2], "Population", df["population"], "f_population")

    mask = (
        df["condition"].isin(condition)
        & df["sample_type"].isin(sample_type)
        & df["treatment"].isin(treatment)
        & df["response"].isin(response)
        & df["sex"].isin(sex)
        & df["time_from_treatment_start"].isin(timepoint)
        & df["population"].isin(population)
    )
    filtered = df[mask]

    if filtered.empty:
        st.warning("No samples match the current filters.")
        return

    st.divider()

    m1, m2, m3 = st.columns(3)
    m1.metric("Samples shown", f"{filtered['sample'].nunique():,}")
    m2.metric("Populations", f"{filtered['population'].nunique()}")
    m3.metric("Rows", f"{len(filtered):,}")

    present = [p for p in POPULATION_ORDER if p in filtered["population"].unique()]

    st.subheader("Mean frequency by population")
    summary = (
        filtered.groupby("population")["percentage"]
        .agg(mean="mean", median="median", std="std", min="min", max="max")
        .reindex(present)
        .round(2)
    )
    c_chart, c_table = st.columns([2, 3])
    c_chart.bar_chart(summary["mean"], horizontal=True)
    c_table.dataframe(summary, use_container_width=True)

    st.subheader("Per-sample frequencies")
    st.caption("One row per sample; each population's frequency (%) in its own column.")
    wide = (
        filtered.pivot_table(index="sample", columns="population", values="percentage")
        .reindex(columns=present)
        .round(2)
    )
    meta = filtered.drop_duplicates("sample").set_index("sample")[
        ["condition", "sample_type", "treatment", "response", "sex", "time_from_treatment_start"]
    ]
    table = meta.join(wide)
    st.dataframe(table, use_container_width=True)
    st.download_button(
        "Download filtered table (CSV)",
        table.to_csv().encode("utf-8"),
        file_name="cell_frequencies_filtered.csv",
        mime="text/csv",
    )
