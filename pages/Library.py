import datetime
import streamlit as st
import pandas as pd
import re
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


def get_library_list_excel_and_date():
    directory_path = 'pages/library/'
    files_in_directory = os.listdir(directory_path)
    excel_files = [file for file in files_in_directory if re.match(r'library_document_list.*\.xlsx$', file)]

    if not excel_files:
        st.error("There's no Excel file in the directory.")
        return None, None

    excel_files_with_time = [(file, os.path.getmtime(os.path.join(directory_path, file))) for file in excel_files]
    excel_files_with_time.sort(key=lambda x: x[1], reverse=True)
    most_recent_file, modification_time = excel_files_with_time[0]
    df = pd.read_excel(os.path.join(directory_path, most_recent_file))

    last_update_date = datetime.datetime.fromtimestamp(modification_time).strftime('%d %B %Y')
    
    return df, last_update_date



st.image("https://raw.githubusercontent.com/dvvilkins/ASK/main/images/ASK_logotype_color.png?raw=true", use_column_width="always")

back = st.button("< Back to App", type="primary")
if back:
    switch_page("prompt_ui")


tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Library", "FAQs", "Product Roadmap", "Feedback"])

with tab1:
    overview = read_markdown_file("pages/ask_overview.md")
    st.markdown(overview, unsafe_allow_html=True)



with tab2:
    df, last_update_date = get_library_list_excel_and_date()
    overview = read_markdown_file("pages/library_overview.md")

    if df is not None:
        num_items = len(df)
        st.markdown("#### Library Overview")
        st.markdown(f"ASK is loaded with **{num_items}** national documents (almost 9000 pages) including USCG Directives, CHDIRAUX documents and documents issued by the USCG Auxiliary National leadership. All these documents are located in public sections of the USCG and USCG Auxiliary websites (cgaux.org uscg.mil).  No secure content is included (i.e., content requiring Member Zone or CAC access. All documents are national. Regional requirements may vary, so check with your local AOR leadership for the final word. ")
        st.markdown(f"{overview}")
        st.markdown("#### Document List")
        st.markdown(f"{num_items} items. Last update: {last_update_date}")  

        # Display the DataFrame
        display_df = df[['source_short']]
        edited_df = st.data_editor(display_df, use_container_width=True, hide_index=False, disabled=True)
        isim = 'ASK_library.csv'
        indir = edited_df.to_csv(index=False)
        b64 = base64.b64encode(indir.encode(encoding='ISO-8859-1')).decode(encoding='ISO-8859-1')  
        linko_final = f'<a href="data:file/csv;base64,{b64}" download={isim}>Click to download</a>'
        st.markdown(linko_final, unsafe_allow_html=True)

    else:
        # Display the original markdown file content if df is None
        overview = read_markdown_file("pages/library_overview.md")
        st.markdown(overview, unsafe_allow_html=True)


with tab3:
    overview = read_markdown_file("pages/faqs.md")
    st.markdown(overview, unsafe_allow_html=True)

with tab4:
    roadmap = read_markdown_file("pages/roadmap.md")
    st.markdown(roadmap, unsafe_allow_html=True)
    
with tab5:
    st.markdown("#### Feedback")
    st.markdown("ASK's mission is to provide USCG Auxiliary members efficient, accuracete and easy access to the authoritative source of knowledge on any topic in the Auxiliary.")
    st.markdown('If you would like to help ASK acheive this mission, **please reach out!**')
                
    st.markdown('''Presently, ASK works by analyzing documents that are the most current official policy that exists at a national level. 
             If you see a document missing from the libary or should be removed, please let us know.''')  
    
    st.markdown('''If you find an error or ommision in a response, please let me know. Be sure to include the exact question asked
             and a reference to the applicable policy (doc and page).''')  
                
    st.markdown('Send an email to uscgaux.drew@wks.us.''')
