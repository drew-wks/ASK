import datetime
import requests
import re
import uuid
import os
from pypdf import PdfReader
import pandas as pd
from dateutil import parser



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



def check_duplicates_in_xlsx(metadata_file_path, cols):
    """
    Function to check for duplicates in specified columns of an Excel file.
    
    Args:
        metadata_file_path (str): The path to the Excel file containing metadata.
        cols (list): List of columns to check for duplicates.
    
    Example usage:
        metadata_file_path = "./docs/metadata/metadata.xlsx"
        cols = ['title', 'publication_number', 'document_id', 'file_name']
        
        check_duplicates_in_xlsx(metadata_file_path, cols)
    
    Returns:
        None
    """
    try:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(metadata_file_path)

        # Iterate over each column and check for duplicates
        for column in cols:
            if column in df.columns:
                # Drop rows with NaN values before checking for duplicates
                non_null_df = df.dropna(subset=[column])
                duplicates = non_null_df[non_null_df.duplicated(subset=column, keep=False)]

                if not duplicates.empty:
                    print(f"Duplicate found in '{column}':")
                    print(duplicates[[column]])
                else:
                    print(f"No duplicates in '{column}'.")
    except Exception as e:
        print(f"An error occurred: {e}")



def compute_pdf_id(pdf_path):
    '''
    Generates a unique ID from the content of the PDF file.

    The function extracts text from all pages of the PDF--ignoring metadata-- and 
    generates a unique ID that is deterministic using UUID v5, so the same content
    will always geenreate the same ID
    example ID:  3b845a10-cb3a-5014-96d8-360c8f1bf63f 
    If the document is empty, then it sets the UUID to "EMPTY_DOCUMENT". 
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        str: UUID for the PDF content or "EMPTY_DOCUMENT" if the PDF is empty.
    '''

    reader = PdfReader(pdf_path)
    num_pages = len(reader.pages)

    # Extract text from all pages and concatenate
    full_text = ""
    for page_num in range(num_pages):
        try:
            page_text = reader.pages[page_num].extract_text()
            if page_text:
                full_text += page_text
        except Exception as e:
            logging.warning(f"Failed to extract text from page {page_num} of {pdf_path}: {e}")

    if not full_text.strip():
        return "EMPTY_DOCUMENT"

    namespace = uuid.NAMESPACE_DNS
    pdf_uuid = uuid.uuid5(namespace, full_text)

    return pdf_uuid



def check_qdrant_record_exists(record_id, qdrant, pdfs_collection_name):
    try:
        result = qdrant.retrieve(
            collection_name=pdfs_collection_name,
            ids=[record_id],  
            with_payload=False,
        )
        if result:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error occurred while checking record existence for ID {record_id}: {e}")
        return False
