''' run by placing this line in terminal
    streamlit run file_name.py
    Easiest in VSCode, "run and debug'. Make sure launch.json is set up
'''

#


import datetime
import streamlit as st
import pandas as pd
from trubrics.integrations.streamlit import FeedbackCollector
import ASK_inference as ASK

from ASK_inference import config
from streamlit_extras.stylable_container import stylable_container
import time
from unittest.mock import patch

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

# === MOCKING START: This section is for mocking and should be removed later ===

# Define dummy return values
dummy_client = "dummy_client"
dummy_qdrant = "dummy_qdrant"
dummy_retriever = "dummy_retriever"
dummy_response = {"result": "dummy_response", "source": "dummy_source"}

# Mock multiple functions at once
with patch.multiple('ASK_inference',
                    qdrant_connect_cloud=lambda x: dummy_client,
                    create_langchain_qdrant=lambda x: dummy_qdrant,
                    init_retriever_and_generator=lambda x: dummy_retriever,
                    rag=lambda x, y: dummy_response):

    # === MOCKING END ===


# Check if 'client' is not in locals() or 'client' is not in globals()
#if not it runs qdrant_check_and_connect()
#and places the client object into st.session_state
if 'clientkey' not in st.session_state:
    st.session_state.clientkey = []
    client = ASK.qdrant_connect_cloud(api_key)
    st.session_state.clientkey = client
    print(st.session_state.clientkey)


qdrant = ASK.create_langchain_qdrant(st.session_state.clientkey)
retriever = ASK.init_retriever_and_generator(qdrant)

collector = FeedbackCollector(
    project="ASK Test on St CC",
    email=st.secrets.TRUBRICS_EMAIL,
    password=st.secrets.TRUBRICS_PASSWORD,
)
# see feedback at https://trubrics.streamlit.app/?ref=blog.streamlit.io



st.image("https://raw.githubusercontent.com/dvvilkins/ASK/main/images/ASK_logotype_color.png?raw=true", use_column_width="always")
# st.title("ASK Auxiliary Source of Knowledge")
st.write(
    "#### Get answers to USCG Auxiliary questions from the authoritative sources.")

st.write("ASK uses Artificial Intelligence (AI) to search over 300 Coast Guard Auxiliary references to answer your questions. The reference list is [here](https://github.com/dvvilkins/ASK/blob/0e975f41f8f072aac2837ac42a9fe11963dc3fb2/docs/library_doc_list.pdf). Have questions? Contact [Drew Wilkins](mailto:uscgaux.drew@wks.us)", unsafe_allow_html=True)
examples = st.empty()

examples.write("""  
    **ASK can answer questions such as:**   
    *What are the requirements to run for FC?*  
    *How do I stay current as a vessel examiner?*   
    *Make a 10 question quiz on boat crewmember tasks, with answers.*   
    
""")
st.write("  ")
st.write("  ")

user_feedback = " "
#response = {}
query = st.chat_input("Type your question or task here", max_chars=200)
if query:
    print(f"Response start {datetime.datetime.now().strftime('%H:%M:%S')}")
    response = ASK.rag(query,retriever)
    print(f"Response finish {datetime.datetime.now().strftime('%H:%M:%S')}")
    short_source_list = ASK.create_short_source_list(response)
    long_source_list = ASK.create_long_source_list(response)
    examples.empty()
    st.info(f"""##### Response:\n{response['result']}\n\n **Sources:**  \n {short_source_list}\n**Note:**  \nASK may contain inaccuracies. Please review the official documents. Also, ASK only searches natonal documents. Check with your district, division and flotilla leadership for official policy in your AOR.
    """)
    #old results expander went here
###############
    with st.status("Compiling references...", expanded=False) as status:
        time.sleep(1)
        st.write(long_source_list)
        status.update(label=":blue[**Click for references**]", expanded=False)

################
    collector.log_prompt(
        config_model={"model": "gpt-3.5-turbo"},
        prompt=query,
        generation=response['result'],
    )


st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")

with stylable_container(
    key="bottom_content",
    css_styles="""
        {
            position: fixed;
            bottom: 0px;
            background-color: rgba(255, 255, 255, 1)
        }
        """,
):
    # st.caption("C")  # this appears above the chat_input() element.
    st.write("where does this appear?")

