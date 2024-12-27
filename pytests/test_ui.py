from streamlit.testing.v1 import AppTest
import time

#requries streamlit version >=1.18
    
def test_ui():
    """
    Test case for the Streamlit user interface I/O using streamlit testing framework AppTest.

    This test performs the following steps:
    1. Initializes the Streamlit app using `AppTest.from_file` with the `ui.py` script.
    2. Runs the app and verifies it starts without exceptions.
    3. Simulates user input by entering a question into the text input field to test
       the app's response to a typical query, "How do I stay current in boat crew?"
    4. Checks for any exceptions during user input simulation and verifies that 
       the app processed the input without errors.
    5. Retrieves the app's response and asserts that it contains the keyword "Response,"
       indicating that the app provided feedback to the query in the expected format.
    6. Returns "tests/test_ui.py::test_ui PASSED"  in the console if the test passes.

    Passing this test confirms:
    - The app can load and run without errors.
    - User input can be entered and processed.
    - The app generates an output response in the expected format.

    Raises:
        AssertionError: If any of the steps result in an unexpected outcome or if
                        exceptions occur during app loading or input processing.
    """
    print("Starting AppTest")
    at = AppTest.from_file("ui.py", default_timeout=5)
    print("Running AppTest")
    at.run()
    
    # Confirm the available text inputs and use the correct one
    print("Available text inputs:", at.text_input)
    at.text_input[0].input("How do I stay current in boat crew?").run(timeout=10)
    
    assert not at.exception, f"An exception occurred: {at.exception}"
    print("No exceptions occurred after mocking user input")
    
    first_response = at.info[0].value
    assert "Response" in first_response  # Check if the response is shown in the info box
    print("Test completed successfully")