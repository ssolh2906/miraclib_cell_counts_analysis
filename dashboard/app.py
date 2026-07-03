import streamlit as st

from sections import frequencies, overview, stats, subset

st.set_page_config(page_title="miraclib cell counts", layout="wide")

overview.render()
frequencies.render()
stats.render()
subset.render()
