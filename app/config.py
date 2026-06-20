"""Streamlit configuration and setup."""

import streamlit as st

st.set_page_config(
    page_title="Biomedical Signal Platform",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com",
        "Report a bug": "https://github.com",
        "About": "Professional Biomedical Signal Visualization Platform v2.0"
    }
)

st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .clinical-header {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)
