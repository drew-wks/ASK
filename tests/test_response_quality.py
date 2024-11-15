import os
import pytest

# Add the parent directory to sys.path so you can import library_utils from a subdirectory
parent_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
    
import utils, rag
from rag import CONFIG


# LANGSMITH CONFIG
# These have to be set as environmental variables to be accessed behind the scenes

os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "test_response_quality"



def load_questions_from_file(filename="user_questions.txt"):
    with open(filename, "r") as file:
        questions = [line.strip() for line in file if line.strip()]
    return questions
]

@pytest.mark.parametrize("question", questions)
def test_rag_pipeline_responses(question):

    response, enriched_question = rag.rag(question)
    
    # Assert the response is not empty
    assert response, f"Response for question '{question}' is empty."

    # Further assertions can be added based on expected response format or keywords
    # assert "expected_keyword" in response, f"Expected keyword not found in response for question '{question}'."

# Run this test file with `pytest` to validate the responses for each question
