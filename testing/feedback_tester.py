import os
import uuid
import streamlit as st
from streamlit_feedback import streamlit_feedback
from langsmith import Client
import rag


# Config LangSmith if you also want the traces
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langchain_user_feedback_tester.ipynb on ASK main/local"


ls_client = Client()  # Defaults to the LANGCHAIN_API_KEY environment variable

def langsmith_feedback(feedback_data):
    """Send feedback to LangSmith."""
    score = 1.0 if feedback_data["score"] == "👍" else 0.0
    run_id = st.session_state.get("run_id")  # Retrieve the run_id from session state
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

# Streamlit app UI
st.title("Chat with the LLM")
user_question = st.text_input("Enter your question:")

# Generate the response only if the question is new
if "response" not in st.session_state and user_question:
    run_id = str(uuid.uuid4())
    st.session_state["run_id"] = run_id
    st.session_state["response"] = cached_rag(user_question, run_id)
    
if "response" in st.session_state:
    response = st.session_state["response"]
    st.info(f"**Question:** {user_question}\n\n**Response:** {response}")

    # Show feedback widget once a response is returned
    feedback_data = streamlit_feedback(
        feedback_type="thumbs", optional_text_label="(Optional) Please explain your rating, so we can improve ASK", align="flex-start")

    if feedback_data:
        st.write("Thanks for the feedback!")
        langsmith_feedback(feedback_data)