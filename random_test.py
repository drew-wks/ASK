import streamlit as st
import random

st.title("Random Number Generator")

random_number = random.randint(1, 100)
st.write(random_number)
    
user_question = st.text_input("Type something here", max_chars=200) 
if user_question:
    with st.status("show the random number...", expanded=False) as status:
        st.write(random_number)
        status.update(label=":blue[number ready!]", expanded=False)
