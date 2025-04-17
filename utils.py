import os
import datetime
import requests
import pandas as pd
import streamlit as st 
from fnmatch import fnmatch
import re




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
        chat_component = next(
            (component for component in components if component.get('name', '').lower() == 'chat'), 
            None
        )
            
        if chat_component:
            status_message = chat_component.get('status', 'unknown')
            return f"ChatGPT API status: {status_message}" if status_message != 'operational' else "ChatGPT API is operational"
        else:
            return "ChatGPT API component not found"

    except requests.exceptions.HTTPError as http_err:
        return f"API check failed (HTTP error): {repr(http_err)}"
    except requests.exceptions.Timeout:
        return "API check timed out"
    except requests.exceptions.RequestException as req_err:
        return f"API check failed (Request error): {repr(req_err)}"
    except Exception as err:
        return f"API check failed (Unknown error): {repr(err)}"




@st.cache_data
def get_library_catalog_excel_and_date():
    """
    Retrieves the most recent Excel file matching the pattern 'docs_report_qdrant_cloud*.xlsx'
    from the 'docs/library_catalog/' directory. The function returns the file as a Pandas 
    DataFrame along with the timestamp from the filename in ISO 8601 format.

    Returns:
        tuple: (DataFrame, str) - The DataFrame containing the Excel file data and
        the timestamp from the filename as a string in the format 'YYYY-MM-DDTHH:MM:SSZ'.
        Returns (None, None) if no matching file is found or if an error occurs.
    """
    # defined here becuase function is accessed in several places. Use full path
    directory_path = './docs/library_catalog/'
    
    try:
        files_in_directory = os.listdir(directory_path)
    except FileNotFoundError:
        os.write(1, b"Directory not found.\n")
        return None, None

    # Use fnmatch for filename matching
    excel_files = [file for file in files_in_directory if fnmatch(file, "docs_report_qdrant_cloud*.xlsx")]
    if not excel_files:
        os.write(1, b"There is no matching Excel file in the directory.\n")
        return None, None

    # Function to extract the timestamp from a filename.
    def extract_timestamp(filename):
        # Expecting filename like: docs_report_qdrant_cloud_YYYY-MM-DDTHHMMSSZ.xlsx
        match = re.search(r'docs_report_qdrant_cloud_(\d{4}-\d{2}-\d{2}T\d{6}Z)\.xlsx', filename)
        if match:
            date_str = match.group(1)  # e.g., "2025-03-14T141504Z"
            try:
                dt = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H%M%SZ')
                return dt
            except Exception:
                return None
        return None

    # Build a list of tuples (filename, extracted_timestamp) and filter out any that don't parse
    excel_files_with_time = []
    for file in excel_files:
        ts = extract_timestamp(file)
        if ts:
            excel_files_with_time.append((file, ts))
    
    if not excel_files_with_time:
        os.write(1, b"None of the Excel files have a valid timestamp in their filename.\n")
        return None, None

    # Sort files by the extracted timestamp, most recent first
    excel_files_with_time.sort(key=lambda x: x[1], reverse=True)
    most_recent_file, file_timestamp = excel_files_with_time[0]

    try:
        df = pd.read_excel(os.path.join(directory_path, most_recent_file))
    except Exception as e:
        os.write(1, f"Failed to read the Excel file: {e}\n".encode())
        return None, None

    # Format the timestamp from the filename to ISO 8601 (with colons)
    last_update_date = file_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
    return df, last_update_date




def main():
    print("Running utils.py directly")
    # You can include test code for utility functions here, if desired

if __name__ == "__main__":
    main()