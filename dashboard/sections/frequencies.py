import streamlit as st

from components.data_loading import load_cell_frequencies


def render() -> None:
    st.header("Cell frequencies")
    st.dataframe(load_cell_frequencies(), use_container_width=True)