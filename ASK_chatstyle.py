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

from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb


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
st.write("ASK uses Artificial Intelligence (AI) to search over 300 Coast Guard Auxiliary references to answer your questions. The reference list is [here](https://github.com/dvvilkins/ASK/blob/0e975f41f8f072aac2837ac42a9fe11963dc3fb2/docs/library_doc_list.pdf).", unsafe_allow_html=True)
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



def image(src_as_string, **style):
    return img(src=src_as_string, style=styles(**style))


def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)


def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
     .stApp { bottom: 105px; }
    </style>
    """

    style_div = styles(
        position="fixed",
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        color="black",
        text_align="center",
        height="auto",
        opacity=1
    )

    style_hr = styles(
        display="block",
        margin=px(8, 8, "auto", "auto"),
        border_style="inset",
        border_width=px(2)
    )

    body = p()
    foot = div(
        style=style_div
    )(
        hr(
            style=style_hr
        ),
        body
    )

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)

        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)


def footer():
    myargs = [
        "Made in ",
        image('https://avatars3.githubusercontent.com/u/45109972?s=400&v=4',
              width=px(25), height=px(25)),
        " with ❤️ by ",
        link("https://twitter.com/ChristianKlose3", "@ChristianKlose3"),
        br(),
        link("https://buymeacoffee.com/chrischross", image('https://i.imgur.com/thJhzOO.png')),
    ]
    layout(*myargs)