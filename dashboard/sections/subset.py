import streamlit as st

from components.data_loading import load_baseline_samples, load_cohort_counts, load_population_means


def render() -> None:
    st.header("Baseline subset (melanoma + miraclib + PBMC, t=0)")

    means = load_population_means()
    headline = means.loc[
        (means["sex"] == "M") & (means["response"] == "yes") & (means["population"] == "b_cell"),
        "mean_cell_count",
    ].iloc[0]
    st.metric("Mean B cells — melanoma males, responders, baseline", f"{headline:.2f}")

    baseline_samples = load_baseline_samples()
    st.subheader("Identified samples")
    st.caption(f"{len(baseline_samples)} samples")
    st.dataframe(baseline_samples, use_container_width=True)

    st.subheader("Cohort composition")
    st.dataframe(load_cohort_counts(), use_container_width=True)

    st.subheader("Population means by sex and response")
    st.dataframe(means, use_container_width=True)
