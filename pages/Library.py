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

back = st.button("< Back to App", type="primary")
if back:
    switch_page('ASK_chatstyle')


tab1, tab2, tab3 = st.tabs(["Library Overview", "Document List", "Suggest a Doc"])

with tab1:
   overview = read_markdown_file("docs/library_overview.md")
   st.markdown(overview, unsafe_allow_html=True)

with tab2:
   st.markdown("#### Document List")

   df = pd.DataFrame(
        [
            {"command": "st.selectbox", "rating": 4, "is_widget": True},
            {"command": "st.balloons", "rating": 5, "is_widget": False},
            {"command": "st.time_input", "rating": 3, "is_widget": True},
        ]
   )

   edited_df = st.data_editor(df)

   favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]


with tab3:
   st.markdown("#### Document Upload")
   st.write("This is a placeholder page for suggesting new documents to add to the ASK Library")
   st.write("Overview of criteria and process")
   st.write("Upload widget here")



