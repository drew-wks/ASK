import datetime
import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
from pathlib import Path

st.set_page_config(page_title="ASK Library", initial_sidebar_state="collapsed")

st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: visible;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 1rem;
                    padding-left: 3rem;
                    padding-right: 3rem;
                }
        </style>
        """, unsafe_allow_html=True)

def read_markdown_file(markdown_file):
   return Path(markdown_file).read_text()


st.title("ASK Document Library")

want_to_contribute = st.button("Return to the App")
if want_to_contribute:
    switch_page('ASK_chatstyle')


tab1, tab2, tab3 = st.tabs(["Library Overview", "Document List", "Owl"])

with tab1:
   overview = read_markdown_file("docs/library_overview.md")
   st.markdown(overview, unsafe_allow_html=True)


with tab2:
   st.header("Document List")
   st.image("https://static.streamlit.io/examples/dog.jpg", width=200)

with tab3:
   st.header("An owl")
   st.image("https://static.streamlit.io/examples/owl.jpg", width=200)





