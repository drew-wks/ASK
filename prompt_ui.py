import streamlit as st 
from trubrics.integrations.streamlit import FeedbackCollector
import ASK_inference as ASK
from ASK_inference import config
import datetime, time
from streamlit_extras.stylable_container import stylable_container


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


qdrant_connect_cloud_cached = st.cache_resource(ASK.qdrant_connect_cloud)
api_key = st.secrets.QDRANT_API_KEY
url = st.secrets.QDRANT_URL
# client = ASK.qdrant_connect_cloud(api_key, url) # use this for ask-test so you can see the changes
client = qdrant_connect_cloud_cached(api_key, url) # use this version for ask-main for speed
qdrant = ASK.create_langchain_qdrant(client)
retriever = ASK.init_retriever_and_generator(qdrant)


# Manage Trubrics authentication token with session state
# see feedback at https://trubrics.streamlit.app/?ref=blog.streamlit.io
if 'trubrics_collector' not in st.session_state:
    try:
        st.session_state.trubrics_collector = FeedbackCollector(
            project="default",
            email=st.secrets.TRUBRICS_EMAIL,
            password=st.secrets.TRUBRICS_PASSWORD,
        )
    except Exception as e:
        st.error(f"Error authenticating with Trubrics: {e}")
        st.stop()

collector = st.session_state.trubrics_collector



st.image("https://raw.githubusercontent.com/dvvilkins/ASK/main/images/ASK_logotype_color.png?raw=true", use_column_width="always")


api_status_message = ASK.get_openai_api_status()
if "operational" not in api_status_message:
    st.error(f"ASK is currently down due to OpenAI {api_status_message}.")
else: st.write("#### Get answers to USCG Auxiliary questions from authoritative sources.")

df, last_update_date = ASK.get_library_doc_catalog_excel_and_date()
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

user_feedback = " "
user_question = st.text_input("Type your question or task here", max_chars=200)
if user_question:
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

    collector.log_prompt(
        config_model={"model": "gpt-3.5-turbo"},
        prompt=query,
        generation=response['result'],
        )
    

    user_feedback = collector.st_feedback(
        component="default",
        feedback_type="thumbs",
        open_feedback_label="[Optional] Provide additional feedback",
        model="gpt-3.5-turbo",
        prompt_id=None,  # checkout collector.log_prompt() to log your user prompts
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
