import uuid
import os
from pypdf import PdfReader



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



def compute_doc_id(pdf_path):
    '''
    Generates a unique ID from the content of the PDF file.

    The function extracts text from all pages of the PDF--ignoring metadata-- and 
    generates a unique ID using UUID v5, example:  3b845a10-cb3a-5014-96d8-360c8f1bf63f 
    If the document is empty, then it sets the UUID to "EMPTY_DOCUMENT". 
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        str: UUID for the PDF content or "EMPTY_DOCUMENT" if the PDF is empty.
    '''

    reader = PdfReader(download_folder)
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
    doc_uuid = uuid.uuid5(namespace, full_text)

    return doc_uuid

