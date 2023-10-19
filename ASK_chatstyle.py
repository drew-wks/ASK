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
from streamlit_extras.stylable_container import stylable_container

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


st.image("https://raw.githubusercontent.com/dvvilkins/ASK/main/images/ASK_logotype_color.png?raw=true", use_column_width="always")
# st.title("ASK Auxiliary Source of Knowledge")
st.write(
    "#### Get answers to USCG Auxiliary questions from the authoritative sources.")
st.write("ASK uses Artificial Intelligence (AI) to search over 300 Coast Guard Auxiliary references to answer your questions. The reference list is [here](https://github.com/dvvilkins/ASK/blob/0e975f41f8f072aac2837ac42a9fe11963dc3fb2/docs/library_doc_list.pdf). Have questions? Contact [Drew Wilkins](mailto:uscgaux.drew@wks.us)", unsafe_allow_html=True)
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
    st.write("")
    st.write("")
    st.write("How well did Ask respond to your question?")
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


with stylable_container(
    key="bottom_content",
    css_styles="""
        {
            position: fixed;
            bottom: 5px;
        }
        """,
):
    st.caption("ASK is not perfect and may contain inaccuracies, so please reading the official documents referenced below each response. Also, ASK only searches natonal documents, so be sure to check with your district, division and flotilla leadership for official policy in your AOR.")  # this appears above the chat_input() element.
    st.write("")
st.markdown(
    """
    <style>
        .stChatFloatingInputContainer {
            bottom: 80px;
            background-color: rgba(0, 0, 0, 0)
        }
    </style>
    """,
    unsafe_allow_html=True,
)

