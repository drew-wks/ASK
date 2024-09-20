from streamlit.testing.v1 import AppTest
import pytest
import time
import sys
import os

# Add the parent directory to sys.path to import rag_qdrant_lc
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


"""
Automated testing script for Streamlit app.

This script tests the following functionalities:
1. Simulates a user typing questions into the prompt field.
2. Verifies that responses are correctly generated based on user input.
3. Ensures that the second input is entered after the first response is rendered.
4. Prints each response to the console.
5. Checks that the list of sources is displayed alongside each response.

Test Cases:
- User types the question "What are the requirements to run for FC?" and receives a response with a list of sources.
- After the first response is rendered, the user types the second question "How do I stay current in boat crew?" and receives another response with sources.

Usage:
- Install the required dependencies using 'pip install pytest streamlit'.
- Change the directory to your project cd ASK
- Run the test using the command 'pytest tests/test_ui.py' to execute all the test cases.
"""

def test_user_query_response():
    # Adjust path to locate 'prompt_ui.py' in the parent directory
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'prompt_ui.py'))
    
    # Load and run the app from prompt_ui.py
    at = AppTest.from_file(script_path).run()

    # Simulate the user typing the first question into the input box
    at.text_input[0].input("What are the requirements to run for FC?").run()

    # Wait to ensure the app has time to process the response (15 seconds)
    time.sleep(15)

    # Assert that the first response and sources are displayed
    first_response = at.info[0].value
    assert "response" in first_response  # Check if the response is shown in the info box
    assert "Sources" in first_response   # Check if the sources are included in the info box

    # Print the first response to the console
    print("First Response:", first_response)

    # Simulate the user typing the second question after the first response
    at.text_input[0].input("How do I stay current in boat crew?").run()

    # Wait again to ensure the app has time to process the second response (15 seconds)
    time.sleep(15)

    # Assert that the second response and sources are displayed
    second_response = at.info[1].value
    assert "response" in second_response
    assert "Sources" in second_response

    # Print the second response to the console
    print("Second Response:", second_response)

if __name__ == "__main__":
    pytest.main()
