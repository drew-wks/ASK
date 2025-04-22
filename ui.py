import streamlit as st
st.set_page_config(page_title="ASK Auxiliary Source of Knowledge", initial_sidebar_state="collapsed")
import os  # needed for local testing
import uuid
from streamlit_feedback import streamlit_feedback
from langsmith import Client



# Config LangSmith
os.environ["LANGCHAIN_API_KEY_ASK"] = st.secrets["LANGCHAIN_API_KEY"] # check which account you are using
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "ui.py on ASK main/cloud" # use this for local testing
# os.environ["LANGCHAIN_PROJECT"] = "ASK Production App (ui.py on ASK main/origin)"

import rag
import utils
from streamlit_extras.stylable_container import stylable_container
from langsmith import traceable


st.markdown(utils.COLLAPSED_CONTROL, unsafe_allow_html=True)
st.markdown(utils.HIDE_STREAMLIT_UI, unsafe_allow_html=True)
st.markdown(utils.BLOCK_CONTAINER_2, unsafe_allow_html=True)
st.image(utils.LOGO, use_container_width=True)


# Check Open AI service status
api_status_message = utils.get_openai_api_status()
if "operational" not in api_status_message:
    st.error(f"ASK is currently down due to OpenAI issue: '{api_status_message}.'")
else: 
    st.write("#### Get answers to USCG Auxiliary questions from authoritative sources.")


# Get the library catalog
df, last_update_date = utils.get_library_catalog_excel_and_date()
num_items = len(df)


# Main app body copy
st.markdown(f"ASK uses Artificial Intelligence (AI) to search {num_items} Coast Guard Auxiliary references for answers. This is a working prototype for evaluation. Not an official USCG Auxiliary service. Learn more <a href='Library' target='_self'><b>here</b></a>.", unsafe_allow_html=True)
example_questions = st.empty()
example_questions.write("""  
    **ASK can answer questions such as:**   
    *What are the requirements to run for FC?*  
    *How do I stay current in boat crew?*   
    *¿En que ocasiones es necesario un saludo militar?*   
    
""")
st.write("  ")


ls_client = Client(api_key=st.secrets["LANGCHAIN_API_KEY"])


def langsmith_feedback(feedback_data):
    """Send user feedback to LangSmith."""
    score = 1.0 if feedback_data["score"] == "👍" else 0.0
    run_id = st.session_state.get("run_id")  # 👈  Retrieve the run_id from session state
    if run_id:
        # st.write(f"Sending feedback for run_id: {run_id}")
        ls_client.create_feedback(
            run_id=run_id,
            key="user_feedback",
            score=score,
            comment=feedback_data["text"],
        )
    else:
        st.warning("Run ID not found. Feedback not sent.")


@st.cache_data(show_spinner=False)
def cached_rag(question, run_id):
    """Wrapper to run the RAG pipeline with caching & feedback support."""
    return rag.rag(question, langsmith_extra={"run_id": run_id})


# Initialize session state variables
if "run_id" not in st.session_state:
    st.session_state["run_id"] = None
if "user_question" not in st.session_state:
    st.session_state["user_question"] = None
if "response" not in st.session_state:
    st.session_state["response"] = None
if "filter_conditions" not in st.session_state:
    st.session_state.filter_conditions = {}
st.sidebar.markdown("#### Experimental\n\n  The following features are experimental and may not work as expected.\n\n")
exclude_expired = st.sidebar.checkbox("Exclude expired documents", value=False)
if exclude_expired:
    st.session_state.filter_conditions["exclude_expired"] = True
else:
    st.session_state.filter_conditions.pop("exclude_expired", None)

st.sidebar.caption("This excludes the Auxiliary Manual along with all Commandant Instructions issued more than 12 years ago and ALCOASTs and ALAUXs issued more than one year ago, per COMDTINST 5215.6J.\n\n")
include_d7 = st.sidebar.checkbox("Include District 7 documents in results")
if include_d7:
    st.session_state.filter_conditions.update({
        "scope": "district",
        "unit": "D7"
    })
else:
    # Default to national scope
    st.session_state.filter_conditions.update({
        "scope": "national"
    })
    st.session_state.filter_conditions.pop("unit", None)

# Always include only public release documents
st.session_state.filter_conditions["public_release"] = True

# Just for debug visibility:
filter_conditions = st.session_state.filter_conditions
st.sidebar.write("Current filter_conditions:", filter_conditions)
# Create response container that can be accessed by the RAG as well as the feedback module
status_placeholder = st.empty()


# >>> Main RAG pipeline <<<
user_question = st.text_input("Type your question or task here", max_chars=200)

# On new user_question, clear previous response and feedback
if user_question and (user_question != st.session_state["user_question"]):
    st.session_state["user_question"] = user_question
    st.session_state.pop("response", None)
    st.session_state["run_id"] = str(uuid.uuid4())


    # Generate the response only if the question is new
if st.session_state.get("user_question") and "response" not in st.session_state:
    # Generate a response
    with status_placeholder.status(label="Checking documents...", expanded=False) as response_container:
        st.session_state["response"] = cached_rag(
            st.session_state["user_question"], st.session_state["run_id"]
        )
        # Open response container once responses are ready
        # response_container.update(label=":blue[**Response**]", state="complete", expanded=True)

# Format Response
if st.session_state.get("response"):
    status_placeholder.empty()
    response = st.session_state["response"]
    short_source_list, long_source_list = rag.create_source_lists(response)
    example_questions.empty()  
    st.info(f"**Question:** *{user_question}*\n\n ##### Response:\n{response['answer']}\n\n **Sources:**  \n{short_source_list}\n **Note:** \n ASK can make mistakes. Verify the sources and check your local policies.")

    # Create a container and fill with references
    with st.expander("CLICK HERE FOR FULL SOURCE DETAILS", expanded=False):
        st.write(long_source_list)


    # Show user feedback widget once a response is returned
    user_feedback = streamlit_feedback(
        feedback_type="thumbs",
        optional_text_label="(Optional) Please explain your rating, so we can improve ASK",
        align="flex-start",
        key=f"user_feedback_{st.session_state.run_id}" # 👈 Unique per response to ensure widget resets
    )

    if user_feedback:
        st.write("Thanks for the feedback!")
        langsmith_feedback(user_feedback)

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

st.markdown(utils.FOOTER, unsafe_allow_html=True)
