import datetime
import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="ASK Library")

want_to_contribute = st.button("I want to contribute!")
if want_to_contribute:
    switch_page('Library')