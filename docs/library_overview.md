
 #### Library Overview
 ASK is loaded with over 250 national documents (over 8000 pages). All these documents are located in public sections of the USCG and USCG Auxiliary websites (cgaux.org uscg.mil). No secure content is included (i.e., content requiring Member Zone or CAC access. All documents are national. Regional requirements may vary, so check with your local AOR leadership for the final word. 

#### Document Types

1. **U.S.Coast Guard Directives,** 

3. **CHDIRAUX documents** 

4. **Auxiliary National Documents**

st.markdown("#### Document List")
    df = get_pickle_file()
    display_df = df[['source_short']]
    edited_df = st.data_editor(display_df, use_container_width=True, hide_index=False, disabled=True)
    # favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
    #downloader
    isim= 'ASK_library.csv'
    indir = edited_df.to_csv(index=False)
    b64 = base64.b64encode(indir.encode(encoding='ISO-8859-1')).decode(encoding='ISO-8859-1')  
    linko_final= f'<a href="data:file/csv;base64,{b64}" download={isim}>Click to download</a>'
    st.markdown(linko_final, unsafe_allow_html=True)