import os
import sys
import streamlit as st
st.set_page_config(page_title="ASK Auxiliary Source of Knowledge", initial_sidebar_state="collapsed")
import utils

sys.path.insert(0, utils.parent_dir)


utils.apply_styles()


back = st.button("< Back to App", type="primary")
if back:
    st.switch_page("ui.py")

tos = utils.get_markdown("docs/tos.md")

st.markdown("#### Terms of Service")
st.write("")
st.markdown(f"{tos}")

