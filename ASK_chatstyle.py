''' run by placing this line in terminal
    streamlit run file_name.py
    Easiest in VSCode, "run and debug'. Make sure launch.json is set up
'''

#
import streamlit as st
import pandas as pd
from trubrics.integrations.streamlit import FeedbackCollector
import ASK_inference as ASK

from ASK_inference import config

st.set_page_config(page_title="ASK Auxiliary Source of Knowledge")

hide_st_style = """
            <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 0rem;
                    padding-right: 0rem;
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

if 'wandbkey' not in st.session_state:
    st.session_state.wandbkey = []
    ASK.wandb_connect()
    st.session_state.wandbkey = True
    print(st.session_state.wandbkey)


qdrant = ASK.create_langchain_qdrant(st.session_state.clientkey)
retriever = ASK.init_retriever_and_generator(qdrant)

collector = FeedbackCollector(
    email=st.secrets.TRUBRICS_EMAIL,
    password=st.secrets.TRUBRICS_PASSWORD,
    project="ASK_chatstyle"
)
# see feedback at https://trubrics.streamlit.app/?ref=blog.streamlit.io


st.image("https://raw.githubusercontent.com/dvvilkins/ASK/main/ASK_color.png?raw=true", use_column_width="always")
# st.title("ASK Auxiliary Source of Knowledge")
st.write(
    "#### Get answers to USCG Auxiliary questions from the authoritative sources.")
st.write("ASK uses Artificial Intelligence (AI) to search over 300 Coast Guard Auxiliary references to answer your questions. The reference list is [here](https://drive.google.com/file/d/1BWY5zEg8yKIrS3Tx13VBpSlpPx7rKl25/view?usp=sharing).", unsafe_allow_html=True)
st.write("  ")
st.write("""  
    **ASK can answer questions such as:**   
    *What are the requirements to run for FC?*  
    *How do I stay current as a vessel examiner?*   
    *Make a 10 question quiz on boat crewmember tasks, with answers.*   
    
""")
st.write("  ")
st.write("  ")


query = st.chat_input("Type your question or task here", max_chars=200)
if query:
    response = ASK.rag(query,retriever)
    short_source_list = ASK.create_short_source_list(response)
    long_source_list = ASK.create_long_source_list(response)
    st.info(f"""##### Response:\n{response['result']}\n\n **Sources:**\n {short_source_list}""")
    with st.expander("##### Full Source Details"):
        st.write(long_source_list)
    
   # st.write("How well did Ask respond to your question?")
    user_feedback = collector.st_feedback(
        component="default",
        feedback_type="thumbs",
        open_feedback_label="[Optional] Provide additional feedback",
        model="gpt-3.5-turbo",
        align="flex-end",
        prompt_id=None,  # checkout collector.log_prompt() to log your user prompts
    )

    if user_feedback:
        st.write(user_feedback)
