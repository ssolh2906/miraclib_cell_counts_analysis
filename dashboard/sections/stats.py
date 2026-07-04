import matplotlib.pyplot as plt
import streamlit as st

from components.charts import cliffs_delta_chart, p_value_chart, q_value_chart
from components.data_loading import (
    boxplots_path,
    load_response_stats,
    pca_path,
    roc_curves_path,
)


def render() -> None:
    st.header("Responder vs. non-responder")

    # Order follows the instruction narrative: (1) boxplot comparison, (2) which
    # populations differ significantly + statistical evidence, (3) extra evidence.
    st.subheader("Population frequency: responder vs. non-responder")
    st.image(str(boxplots_path()))
    with st.expander("Statistical meaning"):
        st.caption(
            "Each population's relative frequency, responder vs non-responder. "
            "Distributions that barely overlap hint at a population tied to treatment response."
        )

    st.subheader("Significant populations (baseline, t=0)")
    response_stats = load_response_stats()
    st.dataframe(response_stats, use_container_width=True)

    st.markdown("**Effect size (Cliff's delta)**")
    fig = cliffs_delta_chart(response_stats)
    st.pyplot(fig)
    plt.close(fig)
    with st.expander("Statistical meaning"):
        st.caption(
            "Cliff's delta measures how much the two groups' distributions overlap, from "
            "-1 to +1 (0 = complete overlap). Unlike a p-value, it doesn't shrink just "
            "because the sample is large, so it tells us how big the difference actually is. "
            "By convention, |delta| below ~0.147 is considered negligible (non-significant effect size)."
        )

    st.markdown("**Significance: raw p-value vs. BH-adjusted q-value**")
    c_p, c_q = st.columns(2)
    fig = p_value_chart(response_stats)
    c_p.pyplot(fig)
    plt.close(fig)
    fig = q_value_chart(response_stats)
    c_q.pyplot(fig)
    plt.close(fig)
    with st.expander("Statistical meaning"):
        st.caption(
            "p-value: Mann-Whitney U test per population. q-value: the same p-values after "
            "Benjamini-Hochberg correction for testing 5 populations at once - use q rather "
            "than raw p to call something significant, so false positives aren't over-counted. "
            "By convention, a value below 0.05 is considered statistically significant."
        )

    st.subheader("Additional evidence")
    st.markdown("**Group separation: PCA vs. ROC-AUC**")
    c_pca, c_roc = st.columns(2)
    c_pca.image(str(pca_path()), caption="PCA of population frequencies, colored by response")
    c_roc.image(str(roc_curves_path()), caption="Per-population ROC curves for predicting response")
    with st.expander("Statistical meaning"):
        st.caption(
            "PCA compresses all 5 populations into 2D to see if responders and "
            "non-responders form visually separate clusters. ROC-AUC quantifies, per "
            "population, how well its frequency alone predicts response "
            "(0.5 = chance, 1.0 = perfect separation)."
        )
