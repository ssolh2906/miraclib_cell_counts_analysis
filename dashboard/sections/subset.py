import matplotlib.pyplot as plt
import streamlit as st

from components.charts import melanoma_miraclib_pbmc_baseline_p_value_chart
from components.data_loading import (
    load_cohort_counts,
    load_melanoma_miraclib_pbmc_baseline_response_stats,
    load_melanoma_miraclib_pbmc_baseline_samples,
    load_population_means,
    melanoma_miraclib_pbmc_baseline_boxplots_by_sex_path,
)


def render() -> None:
    st.header("Baseline subset (melanoma + miraclib + PBMC, t=0)")

    means = load_population_means()
    headline = means.loc[
        (means["sex"] == "M") & (means["response"] == "yes") & (means["population"] == "b_cell"),
        "mean_cell_count",
    ].iloc[0]
    st.metric("Mean B cells — melanoma males, responders, baseline", f"{headline:.2f}")

    samples = load_melanoma_miraclib_pbmc_baseline_samples()
    st.subheader("Identified samples")
    st.caption(f"{len(samples)} samples")
    st.dataframe(samples, use_container_width=True)

    st.subheader("Cohort composition")
    st.dataframe(load_cohort_counts(), use_container_width=True)

    st.subheader("Population means by sex and response")
    st.dataframe(means, use_container_width=True)

    st.subheader("Responder vs. non-responder, by sex")
    st.image(str(melanoma_miraclib_pbmc_baseline_boxplots_by_sex_path()))
    with st.expander("Statistical meaning"):
        st.caption(
            "Same population-frequency comparison as Part 3, split by sex. "
            "Percentage-based (not raw cell count) so it stays compositional-comparable "
            "with Part 3 and isn't confounded by per-sample total cell count."
        )

    baseline_response_stats = load_melanoma_miraclib_pbmc_baseline_response_stats()
    st.dataframe(baseline_response_stats, use_container_width=True)

    st.markdown("**Significance: raw p-value, M vs. F**")
    fig = melanoma_miraclib_pbmc_baseline_p_value_chart(baseline_response_stats)
    st.pyplot(fig)
    plt.close(fig)
    with st.expander("Statistical meaning"):
        st.caption(
            "Mann-Whitney U p-value per population, computed separately within each sex. "
            "The q-value column above is the BH-adjusted version (corrected within each sex, "
            "across its 5 populations) - use q rather than raw p to call something significant."
        )
