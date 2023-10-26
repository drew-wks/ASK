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


tab1, tab2, tab3 = st.tabs(["Library Overview", "Document List", "A flag"])

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
   st.markdown(f"Your favorite command is **{favorite_command}** 🎈")

with tab3:
   st.header("An flag")
   st.image("images/flag.png", width=300)






