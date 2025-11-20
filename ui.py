"""Static Streamlit landing page announcing ASK project retirement."""

import streamlit as st

import ui_utils


st.set_page_config(
    page_title="ASK Auxiliary Source of Knowledge",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ui_utils.apply_styles()

st.markdown(
    """
    <div style="font-size: 1.25rem; margin-top: 1.5rem;">
        The ASK project is no longer available for public access. To enquire about other AI projects, contact www.wks.us
    </div>
    """,
    unsafe_allow_html=True,
)
