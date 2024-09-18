import streamlit as st 
from trubrics.integrations.streamlit import FeedbackCollector
import inference as ASK # both scripts must be in same directory for this to work
from inference import config
import utils
import datetime, time
from streamlit_extras.stylable_container import stylable_container


# Collapse the sidebar and hide the sidebar collapse button
st.set_page_config(page_title="ASK Auxiliary Source of Knowledge", initial_sidebar_state="collapsed")
st.markdown( """ <style> [data-testid="collapsedControl"] { display: none } </style> """, unsafe_allow_html=True, )


# Hide Streamlit's default UI elements: Main menu, footer, and header
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


# Initialize the RAG clients and retriver
try:
    # Cache the Qdrant client connection for performance optimization
    vecdb_connect_cloud_cached = st.cache_resource(ASK.qdrant_connect_cloud)
    api_key = st.secrets.QDRANT_API_KEY
    url = st.secrets.QDRANT_URL
    client = vecdb_connect_cloud_cached(api_key, url) # use ASK.vecdb_connect_cloud(api_key, url) instead for ask-test so you can see the changes
    qdrant = ASK.create_langchain_qdrant(client)
    retriever = ASK.init_retriever_and_generator(qdrant)
except Exception as e:
    st.error(f"An error occurred while setting up the Qdrant client: {e}")
    st.stop() 


st.image("https://raw.githubusercontent.com/dvvilkins/ASK/main/images/ASK_logotype_color.png?raw=true", use_column_width="always")

# Check Open AI service status
api_status_message = utils.get_openai_api_status()
if "operational" not in api_status_message:
    st.error(f"ASK is currently down due to OpenAI {api_status_message}.")
else: st.write("#### Get answers to USCG Auxiliary questions from authoritative sources.")


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
    collector = get_feedback_collector()
    query = ASK.query_maker(user_question)
    with st.status("Checking documents...", expanded=False) as status:
        try:
            if query == "pledge":
                response = ASK.rag_dummy(query, retriever)  # ASK.rag_dummy for UNIT TESTING
            else:
                response = ASK.rag(query, retriever)

            short_source_list = ASK.create_short_source_list(response)
            long_source_list = ASK.create_long_source_list(response)

        except openai.error.RateLimitError:
            print("ASK has run out of Open AI credits. Tell Drew to go fund his account! uscgaux.drew@wks.us")
            response = None  

        except Exception as e:
            print(f"An error occurred: {e} Please try ASK again later")
            response = None  

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
