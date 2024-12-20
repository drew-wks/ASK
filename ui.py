import streamlit as st
import os

# Collapse the sidebar
st.set_page_config(page_title="ASK Auxiliary Source of Knowledge", initial_sidebar_state="collapsed")


import rag
import utils
from streamlit_extras.stylable_container import stylable_container


# Config LangSmith
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "ASK_main"


# Hide Streamlit's default UI elements: Main menu, footer, and header
st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )

hide_streamlit_ui = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_ui, unsafe_allow_html=True)


# Adjust padding around the main content area for a cleaner layout
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


# Banner image
st.image("https://raw.githubusercontent.com/drew-wks/ASK/main/images/ASK_logotype_color.png?raw=true", use_container_width=True)


# Check Open AI service status
api_status_message = utils.get_openai_api_status()
if "operational" not in api_status_message:
    st.error(f"ASK is currently down due to OpenAI {api_status_message}.")
else: 
    st.write("#### Get answers to USCG Auxiliary questions from authoritative sources.")


# Get the library catalog
df, last_update_date = utils.get_library_catalog_excel_and_date()
num_items = len(df)


# Main app body copy
st.markdown(f"ASK uses Artificial Intelligence (AI) to search over {num_items} Coast Guard Auxiliary references for answers. This is a working prototype for evaluation. Not an official USCG Auxiliary service. Learn more <a href='Library' target='_self'><b>here</b>.</a>", unsafe_allow_html=True)
example_questions = st.empty()
example_questions.write("""  
    **ASK answers questions such as:**   
    *What are the requirements to run for FC?*  
    *How do I stay current in boat crew?*   
    *¿En que ocasiones es necesario un saludo militar?*   
    
""")
st.write("  ")


# Prevent user interactions from accidently triggering a re-run
@st.cache_data(show_spinner=False)
def run_cached_rag(question):
    return rag.rag(question)


# Main RAG pipeline
user_question = st.text_input("Type your question or task here", max_chars=200)
if user_question:

    # Create response container
    with st.status("Checking documents...", expanded=False) as response_container:
        response = run_cached_rag(user_question)
        short_source_list = rag.create_short_source_list(response)
        long_source_list = rag.create_long_source_list(response)
        example_questions.empty()  
        st.info(f"**Question:** *{user_question}*\n\n ##### Response:\n{response['answer']['answer']}\n\n **Sources:**  \n{short_source_list}\n **Note:** \n ASK can make mistakes. Verify the sources and check your local policies.")

    # Open response container once responses are ready
    response_container.update(label=":blue[**Response**]", expanded=True)

    # Create a container and fill with references
    with st.status("CLICK HERE FOR FULL SOURCE DETAILS", expanded=False) as references_container:
        st.write(long_source_list)
        # st.write(enriched_question)



# Lock the chat input container 50 pixels above bottom of viewport
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
