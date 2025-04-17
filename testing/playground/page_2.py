import streamlit as st

st.title("Page 2")
st.session_state.unit
back = st.button("< Back to Page 1", type="primary")
if back:
    st.switch_page("page_1.py")