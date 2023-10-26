import datetime
import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="ASK Library", initial_sidebar_state="collapsed")


st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )

st.title("//ASK")
st.write("## Document Library")

want_to_contribute = st.button("Return to the App")
if want_to_contribute:
    switch_page('ASK_chatstyle')


tab1, tab2, tab3 = st.tabs(["Overview", "Document List", "Owl"])

with tab1:
   st.header("Library Overview")
   st.image("https://static.streamlit.io/examples/cat.jpg", width=200)

with tab2:
   st.header("Document List")
   st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

with tab3:
   st.header("An owl")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)