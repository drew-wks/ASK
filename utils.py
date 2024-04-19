import datetime
import requests
import re
import uuid
import os
from pypdf import PdfReader
import pandas as pd
import streamlit as st
from dateutil import parser
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
    regex_pattern = rf'{base_filename}_\d{{4}}-\d{{2}}-\d{{2}}T\d{{4}}Z\.{file_extension}$'
    matching_files = [file for file in files_in_directory if re.match(regex_pattern, file)]

    if not matching_files:
        os.write(1, b"There's no matching file in the directory.\n")
        return None, None

    # Sort files based on the date-time in the filename
    matching_files.sort(key=lambda x: parser.parse(x[len(base_filename)+1:len(base_filename)+16]), reverse=True)
    most_recent_file = matching_files[0]
    last_update_date = most_recent_file[len(base_filename)+1:len(base_filename)+16]
    print(f"found the following file(s) {matching_files}")

    return os.path.join(directory_path, most_recent_file), last_update_date



def compute_doc_id(pdf_path):
    '''
    generates a unique UUID from first page of the PDF file
    
    If first page is generic expiration message dated November 2022,
    then set uuid to second page. If the doc is empty, then set uuid to EMPTY DOC
    
    Example usage
    uuid, first_page = compute_doc_id("RBSVP_Handbook_16796_3_Electronic_Signature.pdf")
    '''
    reader = PdfReader(pdf_path)
    first_page = reader.pages[0].extract_text()
    namespace = uuid.NAMESPACE_DNS
    first_page_uuid = uuid.uuid5(namespace, first_page)
    if str(first_page_uuid) == '4ebd0208-8328-5d69-8c44-ec50939c0967':
        first_page_uuid = "EMPTY_DOCUMENT"
    elif str(first_page_uuid) == '20b41567-46aa-5210-9c92-ea491921869f':
        first_page = reader.pages[1].extract_text()
        first_page_uuid = uuid.uuid5(namespace, first_page)

    return first_page_uuid, first_page

