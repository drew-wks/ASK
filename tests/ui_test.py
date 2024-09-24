from streamlit.testing.v1 import AppTest
import time

def test_ui():
    at = AppTest.from_file("ui.py", default_timeout=5)
    
    # if you need to access secrets, do that here before at.run()
    at.run()
    
    # Simulate user input in the text input widget
    at.text_input[0].input("How do I stay current in boat crew?").run(timeout=10)
    assert not at.exception, f"An exception occurred: {at.exception}"
    print("no exceptions occurred after mocking user input")
    
    first_response = at.info[0].value
    assert "Response" in first_response  # Check if the response is shown in the info box

