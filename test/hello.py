import streamlit as st
import uuid
from streamlit_extras.stylable_container import stylable_container



# Generate a random UUID
unique_key = str(uuid.uuid4())

user_feedback = " "
query = st.text_input("Type your question or task here", max_chars=200, key=unique_key)

if query:
    # Display the input text below the text input widget
    st.write(f"You typed: {user_input}")

