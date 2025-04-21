import os
import sys
from pathlib import Path
import streamlit as st
st.set_page_config(page_title="ASK Auxiliary Source of Knowledge", initial_sidebar_state="collapsed")
import utils

sys.path.insert(0, utils.parent_dir)


st.markdown(utils.COLLAPSED_CONTROL, unsafe_allow_html=True)
st.markdown(utils.HIDE_STREAMLIT_UI, unsafe_allow_html=True)
st.markdown(utils.BLOCK_CONTAINER, unsafe_allow_html=True)
st.image(utils.LOGO, use_container_width=True)


back = st.button("< Back to App", type="primary")
if back:
    st.switch_page("ui.py")

tos = utils.get_markdown("docs/tos.md")

st.markdown("#### Terms of Service")
st.write("")
st.markdown(f"{tos}")

