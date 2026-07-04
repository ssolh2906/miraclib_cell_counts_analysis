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

    response_stats = load_response_stats()
    for chart_fn in (cliffs_delta_chart, p_value_chart, q_value_chart):
        fig = chart_fn(response_stats)
        st.pyplot(fig)
        plt.close(fig)
    st.dataframe(response_stats, use_container_width=True)

    st.image(str(boxplots_path()))
    st.image(str(pca_path()), caption="PCA of population frequencies, colored by response")
    st.image(str(roc_curves_path()), caption="Per-population ROC curves for predicting response")
