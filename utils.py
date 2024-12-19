import os
import re
import datetime
import requests
import pandas as pd
import streamlit as st 


@st.cache_data
def get_openai_api_status():
    '''Notify user if OpenAI is down so they don't blame the app'''

    components_url = 'https://status.openai.com/api/v2/components.json'
    status_message = ''

    try:
        response = requests.get(components_url, timeout=10)
        # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()
        components_info = response.json()
        components = components_info.get('components', [])

        # Find the component that represents the API
        api_component = next(
            (component for component in components if component.get('name', '').lower() == 'api'), None)

        if api_component:
            status_message = api_component.get('status', 'unknown')
            if status_message != 'operational':
                return f"API status: {status_message}"
            else:
                return "API is operational"
        else:
            return 'API component not found'

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {repr(http_err)}"
    except Exception as err:
        return f"Error checking API status: {repr(err)}"

        

@st.cache_data
def get_library_doc_catalog_excel_and_date():
    '''Gets the most recent catalog of library documents'''

    directory_path = 'docs/library_catalog/'
    files_in_directory = os.listdir(directory_path)
    excel_files = [file for file in files_in_directory if re.match(r'library_catalog.*\.xlsx$', file)]

    if not excel_files:
        os.write(1,b"There's no Excel file in the directory.\n")
        return None, None

    excel_files_with_time = [(file, os.path.getmtime(os.path.join(directory_path, file))) for file in excel_files]
    excel_files_with_time.sort(key=lambda x: x[1], reverse=True)
    most_recent_file, modification_time = excel_files_with_time[0]
    try:
        df = pd.read_excel(os.path.join(directory_path, most_recent_file))
    except Exception as e:
        print(f"Failed to read the Excel file: {e}")
        return None, None

    last_update_date = datetime.datetime.fromtimestamp(modification_time).strftime('%d %B %Y')
    
    return df, last_update_date


def main():
    print("Running utils.py directly")
    # You can include test code for utility functions here, if desired

if __name__ == "__main__":
    main()