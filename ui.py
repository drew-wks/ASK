import streamlit as st

# Collapse the sidebar
st.set_page_config(page_title="ASK Auxiliary Source of Knowledge", initial_sidebar_state="collapsed")


import rag
import utils
import datetime, time
from streamlit_extras.stylable_container import stylable_container



# Hide Streamlit's default UI elements: Sidebar button (doesn't work), Main menu, footer, and header
st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )

hide_streamlit_ui = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_ui, unsafe_allow_html=True)


# Adjust the padding around the main content area for a cleaner layout
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


st.image("https://raw.githubusercontent.com/dvvilkins/ASK/main/images/ASK_logotype_color.png?raw=true", use_column_width="always")


# Check Open AI service status
api_status_message = utils.get_openai_api_status()
if "operational" not in api_status_message:
    st.error(f"ASK is currently down due to OpenAI {api_status_message}.")
else: 
    st.write("#### Get answers to USCG Auxiliary questions from authoritative sources.")


# Get the library catalog
df, last_update_date = utils.get_library_doc_catalog_excel_and_date()
num_items = len(df)


st.markdown(f"ASK uses Artificial Intelligence (AI) to search over {num_items} Coast Guard Auxiliary references for answers. This is a working prototype for evaluation. Not an official USCG Auxiliary service. Learn more <a href='Library' target='_self'><b>here</b>.</a>", unsafe_allow_html=True)
examples = st.empty()
examples.write("""  
    **ASK answers questions such as:**   
    *What are the requirements to run for FC?*  
    *How do I stay current in boat crew?*   
    *¿En que ocasiones es necesario un saludo militar?*   
    
""")
st.write("  ")


# Accept a user query and run a RAG pipeline
user_feedback = " "
user_question = st.text_input("Type your question or task here", max_chars=200)
if user_question:
    collector = utils.get_feedback_collector()
    query = rag.query_maker(user_question)
    retriever = rag.get_retriever()
    with st.status("Checking documents...", expanded=False) as status:
        if query == "pledge":
            response = rag.rag_dummy(query, retriever)  # rag.rag_dummy for UNIT TESTING
        else:
            response = rag.rag(query, retriever)

        short_source_list = rag.create_short_source_list(response)
        long_source_list = rag.create_long_source_list(response)

        examples.empty()  
        st.info(f"**Question:** *{user_question}*\n\n ##### Response:\n{response['result']}\n\n **Sources:**  \n{short_source_list}\n **Note:** \n ASK can make mistakes. Verify the sources and check your local policies.")

    status.update(label=":blue[**Response**]", expanded=True)

    with st.status("Compiling references...", expanded=False) as status:
        time.sleep(1)
        st.write(long_source_list)
        st.write(query)
        status.update(label=":blue[CLICK HERE FOR FULL SOURCE DETAILS]", expanded=False)

            
    # Send the prompt used and any feedback to Trubrics feedback collector
    collector.log_prompt(
        config_model={"model": "gpt-3.5-turbo"},
        prompt=query,
        generation=response['result'],
        )
    collector.st_feedback(
        component="default",
        feedback_type="thumbs",
        open_feedback_label="[Optional] Provide additional feedback",
        model="gpt-3.5-turbo",
        prompt_id=None,
        )


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
