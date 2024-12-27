import streamlit as st
from streamlit_feedback import streamlit_feedback
from langsmith import Client
import os


# Config LangSmith
# os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT"] = "ASK_main"


def langsmith_feedback(feedback_data):
    ls_client = Client() # Defaults to the LANGCHAIN_API_KEY environment variable
    score = 1.0 if feedback_data["score"] == "👍" else 0.0
    ls_client.create_feedback(
        # project_id="20d1dded-c22f-458a-9915-8f92159e3dfd",
        run_id="d3763856-37c1-4fd0-a34c-bd36207b22c6",
        key="user_feedback",
        score=score,
        comment=feedback_data["text"],
    )


# Streamlit app UI
st.title("Chat with the LLM")
user_question = st.text_input("Enter your question:")

if user_question:
    response = "Simulated LLM response for your input."  # Replace with actual LLM response
    st.info(f"**Question:** {user_question}\n\n**Response:** {response}")

    feedback_data = streamlit_feedback(
        feedback_type="thumbs", optional_text_label="[Optional] Please explain your rating, so we can improve ASK", align="flex-start")
    if feedback_data:
        st.write("Feedback data:", feedback_data)
        langsmith_feedback(feedback_data)



"""    
with st.form('feedback_form'):
        feedback_data = streamlit_feedback(
            feedback_type="thumbs", optional_text_label="[Optional] Please explain your rating, so we can improve ASK", align="flex-start")
        submitted = st.form_submit_button('Save feedback')
        if submitted:
            st.write("Feedback data:", feedback_data)
            # langsmith_feedback(feedback_data)
"""