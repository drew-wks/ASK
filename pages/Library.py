import datetime
import streamlit as st
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
from pathlib import Path
import os
import base64

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



def get_pickle_file(): 
    directory_path = 'reports/library_pkl/'
    files_in_directory = os.listdir(directory_path)
    pickle_files = [file for file in files_in_directory if file.endswith('.pkl')]

    if len(pickle_files) == 1:
        df = pd.read_pickle(os.path.join(directory_path, pickle_files[0]))
        return df
    else:
        st.error("There's either no pickle file or more than one in the directory.")
        return None



st.image("https://raw.githubusercontent.com/dvvilkins/ASK/main/images/ASK_logotype_color.png?raw=true", use_column_width="always")

back = st.button("< Back to App", type="primary")
if back:
    switch_page("ASK_chatstyle")


tab1, tab2, tab3 tab4 = st.tabs(["ASK Overview", "Document Library", "FAQs", "Feedback"])

with tab1:
    overview = read_markdown_file("docs/ask_overview.md")
    st.markdown(overview, unsafe_allow_html=True)


with tab2:
    overview = read_markdown_file("docs/library_overview.md")
    st.markdown(overview, unsafe_allow_html=True)

    df = get_pickle_file()
    display_df = df[['source_short']]
    edited_df = st.data_editor(display_df, use_container_width=True, hide_index=False, disabled=True)
    isim= 'ASK_library.csv'
    indir = edited_df.to_csv(index=False)
    b64 = base64.b64encode(indir.encode(encoding='ISO-8859-1')).decode(encoding='ISO-8859-1')  
    linko_final= f'<a href="data:file/csv;base64,{b64}" download={isim}>Click to download</a>'
    st.markdown(linko_final, unsafe_allow_html=True)

with tab3:
    overview = read_markdown_file("docs/faqs.md")
    st.markdown(overview, unsafe_allow_html=True)

with tab4:
    st.markdown("#### Feedback")
    st.write("ASK works by analyzing documents that are the most current official policy that exists at a national level.")
    st.write("")
    st.write('''If you see a document missing from the libary or should be removed, please let us know.
             Send an email to uscgaux.drew@wks.us.''')
