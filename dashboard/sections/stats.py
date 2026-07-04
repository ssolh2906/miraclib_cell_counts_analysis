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

    st.subheader("Significant populations (baseline, t=0)")
    response_stats = load_response_stats()
    st.dataframe(response_stats, use_container_width=True)

    fig = cliffs_delta_chart(response_stats)
    st.pyplot(fig)
    plt.close(fig)

    c_p, c_q = st.columns(2)
    fig = p_value_chart(response_stats)
    c_p.pyplot(fig)
    plt.close(fig)
    fig = q_value_chart(response_stats)
    c_q.pyplot(fig)
    plt.close(fig)

    st.subheader("Additional evidence")
    c_pca, c_roc = st.columns(2)
    c_pca.image(str(pca_path()), caption="PCA of population frequencies, colored by response")
    c_roc.image(str(roc_curves_path()), caption="Per-population ROC curves for predicting response")
