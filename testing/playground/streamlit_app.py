import streamlit as st


st.sidebar.checkbox("set unit to True", key="unit")

pages = {
    "Your app": [
        st.Page("page_1.py", title="Page 1"),
        st.Page("page_2.py", title="Page 2"),
    ],
}
pg = st.navigation(pages)
pg.run()

