import streamlit as st
import pandas as pd
from trubrics.integrations.streamlit import FeedbackCollector
import ASK_inference as ASK

from ASK_inference import config


collector = FeedbackCollector(
    email=st.secrets.TRUBRICS_EMAIL,
    password=st.secrets.TRUBRICS_PASSWORD,
    project="ASK_chatstyle"
)

   # st.write("How well did Ask respond to your question?")
user_feedback = collector.st_feedback(
    component="default",
    feedback_type="thumbs",
    open_feedback_label="[Optional] Provide additional feedback",
    model="gpt-3.5-turbo",
    align="flex-end",
    prompt_id=None,  # checkout collector.log_prompt() to log your user prompts
)


st.write(user_feedback)
