"""Read pipeline outputs (outputs/*.csv, outputs/*.png) for the dashboard.

Reads plain CSVs directly rather than importing src - streamlit run doesn't
put the repo root on sys.path, only dashboard/ (the script's own directory).
"""

from pathlib import Path

import pandas as pd
import streamlit as st

OUTPUTS_DIR = Path(__file__).resolve().parents[2] / "outputs"


@st.cache_data
def load_cell_frequencies() -> pd.DataFrame:
    return pd.read_csv(OUTPUTS_DIR / "cell_frequencies.csv")


@st.cache_data
def load_response_stats() -> pd.DataFrame:
    return pd.read_csv(OUTPUTS_DIR / "response_stats.csv")


@st.cache_data
def load_melanoma_miraclib_pbmc_baseline_samples() -> pd.DataFrame:
    return pd.read_csv(OUTPUTS_DIR / "melanoma_miraclib_pbmc_baseline_samples.csv")


@st.cache_data
def load_cohort_counts() -> pd.DataFrame:
    return pd.read_csv(OUTPUTS_DIR / "subset_cohort_counts.csv")


@st.cache_data
def load_population_means() -> pd.DataFrame:
    return pd.read_csv(OUTPUTS_DIR / "subset_population_means.csv")


def boxplots_path() -> Path:
    return OUTPUTS_DIR / "boxplots.png"


def pca_path() -> Path:
    return OUTPUTS_DIR / "pca.png"


def roc_curves_path() -> Path:
    return OUTPUTS_DIR / "roc_curves.png"