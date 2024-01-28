from pypdf import PdfWriter, PdfReader
import os

def write_metadata_to_pdfs(pdfs_processed_metadata_dict):
    '''write new metadata values out to pdfs'''
    
    # Ensure the output directory exists
    output_dir = '../data/PDFs_metadata_complete'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file, metadata in pdfs_processed_metadata_dict.items():
        pdf_path = metadata['pdf_path']
        
        # Determine the output path for the updated PDF
        output_path = os.path.join(output_dir, os.path.basename(pdf_path))
        
        # Read the original PDF
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            writer = PdfWriter()
            
            # Copy all the pages to the writer object
            for page_num in range(reader.numPages):
                page = reader.getPage(page_num)
                writer.addPage(page)
            
            # Prepare metadata for writing (excluding only the pdf_path field)
            metadata_to_write = {key: value for key, value in metadata.items() if key != 'pdf_path'}
            
            # Add the metadata to the writer object
            writer.addMetadata(metadata_to_write)
            
            # Write the updated PDF to the new location
            with open(output_path, 'wb') as out:
                writer.write(out)

# Call the function to write metadata to PDFs
write_metadata_to_pdfs(pdfs_processed_metadata_dict)
