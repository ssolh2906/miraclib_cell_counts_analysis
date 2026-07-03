import streamlit as st

from components.data_loading import (
    boxplots_path,
    load_response_stats,
    pca_path,
    roc_curves_path,
)


def render() -> None:
    st.header("Responder vs. non-responder")
    st.dataframe(load_response_stats(), use_container_width=True)
    st.image(str(boxplots_path()))
    st.image(str(pca_path()), caption="PCA of population frequencies, colored by response")
    st.image(str(roc_curves_path()), caption="Per-population ROC curves for predicting response")
