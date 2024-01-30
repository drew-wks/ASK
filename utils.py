import datetime
import requests
import re
import os
import pandas as pd
import streamlit as st
from trubrics.integrations.streamlit import FeedbackCollector


@st.cache_data
def get_feedback_collector():
    return FeedbackCollector(
        project="default",
        email=st.secrets["TRUBRICS_EMAIL"],
        password=st.secrets["TRUBRICS_PASSWORD"]
    )



def get_openai_api_status():
    '''Notify user if OpenAI is down so they don't blame the app'''

    components_url = 'https://status.openai.com/api/v2/components.json'
    status_message = ''

    try:
        response = requests.get(components_url)
        # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        response.raise_for_status()

        # Parse the JSON response
        components_info = response.json()
        components = components_info.get('components', [])

        # Find the component that represents the API
        api_component = next(
            (component for component in components if component.get('name', '').lower() == 'api'), None)

        if api_component:
            status_message = api_component.get('status', '')
        else:
            status_message = 'API component not found'

    except requests.exceptions.HTTPError as http_err:
        status_message = f'HTTP error occurred: {repr(http_err)}'
    except Exception as err:
        status_message = f'Other error occurred: {repr(err)}'

    return status_message



def check_directory_exists(directory_path, create_if_not_exists=False):
    """
    Check if a directory exists. Optionally, create the directory if it does not exist.

    :param directory_path: Path of the directory to check.
    :param create_if_not_exists: If True, creates the directory if it does not exist.
    :return: True if the directory exists or was created, False otherwise.
    """
    if not os.path.isdir(directory_path):
        if create_if_not_exists:
            try:
                os.write(1,f"Directory does not exist: {directory_path}. Creating it.".encode())
                os.makedirs(directory_path)
                return True
            except OSError as error:
                os.write(1,f"Error creating directory {directory_path}: {error}".encode())
                return False
        else:
            os.write(1,f"Directory does not exist: {directory_path}".encode())
            return False
    return True



def get_most_recent_filepath_and_date(base_filename, directory_path, file_extension):
    """
    Returns the path of the most recent file based on the base filename, directory path, and file extension, along with its last modification date.

    This function searches for files matching the base filename pattern with the specified extension in the given directory and identifies the most recent file based on modification time. It also returns the modification time in 'dd Month YYYY' format.
        
    Usage:
        file_path, last_update_date = get_most_recent_file_path_and_date("library_catalog", "docs/library_catalog/", "xlsx")
    """

    check_directory_exists(directory_path, create_if_not_exists=True)
    files_in_directory = os.listdir(directory_path)
    # Construct regex pattern from base filename and file extension
    regex_pattern = rf'{base_filename}.*\.{file_extension}$'
    matching_files = [file for file in files_in_directory if re.match(regex_pattern, file)]

    if not matching_files:
        os.write(1, b"There's no matching file in the directory.\n")
        return None, None

    matching_files_with_time = [(file, os.path.getmtime(os.path.join(directory_path, file))) for file in matching_files]
    matching_files_with_time.sort(key=lambda x: x[1], reverse=True)
    most_recent_file, modification_time = matching_files_with_time[0]

    last_update_date = datetime.datetime.fromtimestamp(modification_time).strftime('%d %B %Y')

    return os.path.join(directory_path, most_recent_file), last_update_date
    