import os
import sys
import streamlit as st
st.set_page_config(page_title="ASK Auxiliary Source of Knowledge", initial_sidebar_state="collapsed")
import ui_utils

sys.path.insert(0, ui_utils.parent_dir)


ui_utils.apply_styles()


back = st.button("< Back to App", type="primary")
if back:
    st.switch_page("ui.py")

tos = ui_utils.get_markdown("docs/tos.md")

st.markdown("#### Terms of Service")
st.write("")
st.markdown(f"{tos}")

