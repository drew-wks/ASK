import datetime
import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="ASK Library")

st.title("//ASK Auxiliary Source of Knowledge")


want_to_contribute = st.button("Return to App")
if want_to_contribute:
    switch_page('ASK_chatstyle')