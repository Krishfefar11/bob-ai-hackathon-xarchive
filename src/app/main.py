"""Streamlit entry point — Drug Safety Signal Detector & Regulatory Submission Readiness Checker."""
import sys
from pathlib import Path

# main.py lives at src/app/main.py — add src/ to sys.path so sibling packages
# (signal_detection, ingestion, submission_checker, llm) are importable.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from mode1_ui import render_signal_detector
from mode2_ui import render_submission_checker

st.set_page_config(
    page_title="Drug Safety & Regulatory Readiness (P2)",
    page_icon="💊",
    layout="wide",
)

with st.sidebar:
    st.markdown("## 💊 P2 Toolkit")
    st.caption("IBM Bob Hackathon — Lablab.ai")
    st.divider()
    st.markdown(
        "**Signal Detector** flags drug-event pairs reported far more than expected "
        "(PRR≥2, χ²≥4, n≥3 — Evans et al. 2001), using live FDA adverse event data."
    )
    st.markdown(
        "**Submission Checker** scores a draft regulatory document against the "
        "ICH M4 CTD structure, module by module."
    )
    st.divider()
    st.markdown("**Data sources**")
    st.caption("[OpenFDA drug event API](https://open.fda.gov/apis/drug/event/)")
    st.caption("[ICH M4 CTD guidelines](https://www.ich.org/page/multidisciplinary-guidelines#4)")
    st.divider()
    st.caption("No client data, PI, or social-media data — public FDA/ICH data only.")

st.title("Drug Safety Signal Detector & Regulatory Submission Readiness Checker")
st.caption("IBM Bob Hackathon — Problem P2 — built on FDA FAERS / OpenFDA + ICH M4 CTD")

tab1, tab2 = st.tabs(["🔍 Signal Detector", "📋 Submission Checker"])

with tab1:
    render_signal_detector()

with tab2:
    render_submission_checker()
