import requests

def check_streamlit_app(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("ASK Streamlit app is up and running!")
        else:
            print("ASK Streamlit app is not reachable. Status code:", response.status_code)
            sys.exit(1)  # Exits with error if status code is not 200
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        sys.exit(1)  # Exits with error if there's an exception


check_streamlit_app('https://uscg-auxiliary-ask.streamlit.app/')
