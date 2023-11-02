import streamlit as st
import uuid
from streamlit_extras.stylable_container import stylable_container



# Generate a random UUID
unique_key = str(uuid.uuid4())

user_feedback = " "
query = st.text_input("Type your question or task here", max_chars=200, key=unique_key)

st.write(query)
st.write("something")

