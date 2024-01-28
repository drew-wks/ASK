import streamlit as st 
import inference
from inference import config
import utils
import datetime, time
from streamlit_extras.stylable_container import stylable_container


st.set_page_config(page_title="inference Auxiliary Source of Knowledge", initial_sidebar_state="collapsed")

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


qdrant_connect_cloud_cached = st.cache_resource(inference.qdrant_connect_cloud)
api_key = st.secrets.QDRANT_API_KEY
url = st.secrets.QDRANT_URL
client = inference.qdrant_connect_cloud(api_key, url) # use this for ask-test so you can see the changes
# client = qdrant_connect_cloud_cached(api_key, url) # use this version for ask-main for speed
qdrant = inference.create_langchain_qdrant(client)
retriever = inference.init_retriever_and_generator(qdrant)
collector = utils.get_feedback_collector()
# see feedback at https://trubrics.streamlit.app/?ref=blog.streamlit.io


st.image("https://raw.githubusercontent.com/dvvilkins/inference/main/images/ASK_logotype_color.png?raw=true", use_column_width="always")


api_status_message = utils.get_openai_api_status()
if "operational" not in api_status_message:
    st.error(f"inference is currently down due to OpenAI {api_status_message}.")
else: st.write("#### Get answers to USCG Auxiliary questions from authoritative sources.")

df, last_update_date = utils.get_library_doc_catalog_excel_and_date()
num_items = len(df)


st.markdown(f"inference uses Artificial Intelligence (AI) to search over {num_items} Coast Guard Auxiliary references for answers. This is a working prototype for evaluation. Not an official USCG Auxiliary service. Learn more <a href='Library' target='_self'><b>here</b>.</a>", unsafe_allow_html=True)

examples = st.empty()

examples.write("""  
    **inference answers questions such as:**   
    *What are the requirements to run for FC?*  
    *How do I stay current in boat crew?*   
    *¿En que ocasiones es necesario un saludo militar?*   
    
""")

st.write("  ")

user_feedback = " "
user_question = st.text_input("Type your question or task here", max_chars=200)
if user_question:
    query = inference.query_maker(user_question)
    with st.status("Checking documents...", expanded=False) as status:
        try:
            if query == "pledge":
                response = inference.rag_dummy(query, retriever)  # inference.rag_dummy for UNIT TESTING
            else:
                response = inference.rag(query, retriever)

            short_source_list = inference.create_short_source_list(response)
            long_source_list = inference.create_long_source_list(response)

        except openai.error.RateLimitError:
            print("inference has run out of Open AI credits. Tell Drew to go fund his account! uscgaux.drew@wks.us")
            response = None  
        examples.empty()  
        st.info(f"**Question:** *{user_question}*\n\n ##### Response:\n{response['result']}\n\n **Sources:**  \n{short_source_list}\n **Note:** \n inference can make mistakes. Verify the sources and check your local policies.")

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
