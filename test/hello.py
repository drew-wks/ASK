import streamlit as st
import uuid


unique_key = "fiya"


query = st.text_input("Type your question or task here", max_chars=200, key=unique_key)

if query:
    st.write(f"You typed: {query}")
    unique_key = str(uuid.uuid4())


