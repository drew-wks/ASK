import requests

def check_streamlit_app(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("ASK Streamlit app is up and running!")
        else:
            print("ASK Streamlit app is not reachable. Status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("An error occurred: ", e)

check_streamlit_app('https://uscg-auxiliary-ask.streamlit.app/')
