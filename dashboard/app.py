import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root -> allow `import src`

import streamlit as st

from sections import frequencies, overview, stats, subset

st.set_page_config(page_title="miraclib cell counts", layout="wide")

pages = [
    st.Page(overview.render, title="Overview", icon="📊", url_path="overview", default=True),
    st.Page(frequencies.render, title="Part 2 · Frequencies", icon="🧬", url_path="frequencies"),
    st.Page(stats.render, title="Part 3 · Stats", icon="📈", url_path="stats"),
    st.Page(subset.render, title="Part 4 · Subset", icon="🔬", url_path="subset"),
]

nav = st.navigation(pages)
nav.run()
