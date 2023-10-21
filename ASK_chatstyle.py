import streamlit as st
import pandas as pd
from trubrics.integrations.streamlit import FeedbackCollector
import ASK_inference as ASK

from ASK_inference import config
from streamlit_extras.stylable_container import stylable_container
import time
print(f"Finish imports {datetime.datetime.now().strftime('%H:%M:%S')}")
print(f"Start css and session states {datetime.datetime.now().strftime('%H:%M:%S')}")
st.set_page_config(page_title="ASK Auxiliary Source of Knowledge")

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

api_key=st.secrets.QDRANT_API_KEY


# Check if 'client' is not in locals() or 'client' is not in globals()
#if not it runs qdrant_check_and_connect()
#and places the client object into st.session_state
if 'clientkey' not in st.session_state:
    st.session_state.clientkey = []
    client = ASK.qdrant_connect_cloud(api_key)
    st.session_state.clientkey = client
    print(st.session_state.clientkey)


print(f"Qdrant start {datetime.datetime.now().strftime('%H:%M:%S')}")
qdrant = ASK.create_langchain_qdrant(st.session_state.clientkey)
print(f"Qdrant finish {datetime.datetime.now().strftime('%H:%M:%S')}")
print(f"Retriever start {datetime.datetime.now().strftime('%H:%M:%S')}")
retriever = ASK.init_retriever_and_generator(qdrant)
print(f"Retriever finish {datetime.datetime.now().strftime('%H:%M:%S')}")


collector = FeedbackCollector(
    email=st.secrets.TRUBRICS_EMAIL,
    password=st.secrets.TRUBRICS_PASSWORD,
    project="ASK_chatstyle"
)

   # st.write("How well did Ask respond to your question?")
user_feedback = collector.st_feedback(
    component="default",
    feedback_type="thumbs",
    model="gpt-3.5-turbo",
    open_feedback_label="[Optional] Provide additional feedback",
    align="flex-end",
    prompt_id=None,  # checkout collector.log_prompt() to log your user prompts
)


st.write(user_feedback)
