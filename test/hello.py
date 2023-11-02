import streamlit as st
import uuid


unique_key = str(uuid.uuid4())


query = st.text_input("Type your question or task here", max_chars=200, key=unique_key)

if query:
    st.write(f"You typed: {query}")


haha = st.text_input("Type your question or task here", max_chars=200)

if haha:
    st.write(f"You typed: {haha}")

