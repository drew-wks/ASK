import streamlit as st 
import datetime
import pandas as pd
from trubrics.integrations.streamlit import FeedbackCollector
import ASK_inference as ASK

from ASK_inference import config
from streamlit_extras.stylable_container import stylable_container
import time
st.set_page_config(page_title="ASK Auxiliary Source of Knowledge", initial_sidebar_state="collapsed")


st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 1rem;
                    padding-left: 2rem;
                    padding-right: 2rem;
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


qdrant = ASK.create_langchain_qdrant(st.session_state.clientkey)
retriever = ASK.init_retriever_and_generator(qdrant)

collector = FeedbackCollector(
    project="ASK Test on St CC",
    email=st.secrets.TRUBRICS_EMAIL,
    password=st.secrets.TRUBRICS_PASSWORD,
)
# see feedback at https://trubrics.streamlit.app/?ref=blog.streamlit.io


st.image("https://raw.githubusercontent.com/dvvilkins/ASK/main/images/ASK_logotype_color.png?raw=true", use_column_width="always")

st.write(
    "#### Get answers to USCG Auxiliary questions from authoritative sources.")

st.markdown("ASK uses Artificial Intelligence (AI) to search over 250 Coast Guard Auxiliary references for answers. Created for evaluation by Drew Wilkins. Not an official USCG Auxiliary service. Learn more <a href='Library' target='_self'>here.</a>", unsafe_allow_html=True)


examples = st.empty()

examples.write("""  
    **ASK answers questions such as:**   
    *What are the requirements to run for FC?*  
    *How do I stay current as a member?*   
    *Make a 10 question quiz on boat crewmember tasks, with answers.*   
    
""")
st.write("  ")

user_feedback = " "
query = st.text_input("Type your question or task here", max_chars=200)
if query:
    with st.status("Checking documents...", expanded=False) as status:
        if query == "pledge":
            response = ASK.rag_dummy(query,retriever) # ASK.rag_dummy for UNIT TESTING
        else:
            response = ASK.rag(query,retriever) 
        short_source_list = ASK.create_short_source_list(response)
        long_source_list = ASK.create_long_source_list(response)
        examples.empty()

        st.info(f"**Question:** *{query}*\n\n ##### Response:\n{response['result']}\n\n **Sources:**  \n{short_source_list}\n**Note:**  \n ASK can make mistakes. Verify the sources and check for local policy. Learn more about ASK<a href='Library' target='_self'>here.</a>")
    status.update(label=":blue[**Response**]", expanded=True)

    with st.status("Compiling references...", expanded=False) as status:
        time.sleep(1)
        st.write(long_source_list)
        status.update(label=":blue[**Click for full references**]", expanded=False)

    collector.log_prompt(
        config_model={"model": "gpt-3.5-turbo"},
        prompt=query,
        generation=response['result'],
    )


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
    st.markdown(
    """
    <style>
        .stChatFloatingInputContainer {
            bottom: 50px;
            background-color: rgba(255, 255, 255, 1)
        }
    </style>
    """,
    unsafe_allow_html=True,
    )
