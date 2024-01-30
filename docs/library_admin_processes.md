## ASK System Administration
#### Adding PDFs to Library
##### 1. Prepare the document metadata (prep_document_metadata.ipynb)
<div style="border: 2px solid black; padding: 10px;">

```mermaid
sequenceDiagram
    actor Curator
    participant System
    participant File Storage
    
    Curator->>System: specify target PDFs to add
    System->>File Storage: copy PDFs to PDF_ingest_queue folder
    System->>System: check PDFs for errors
    System->>System: extract PDF names and existing metadata
    System->>System: add additional metadata    
    File Storage->>System: retrieve latest library_catalog{}.xlsx
    System->>System: check for duplicates
    System->>System: append metadata to library_catalog
    System->>File Storage: output updated library_catalog{}.xlsx
    Curator->>File Storage: add/edit metadata in updated library_catalog{}.xlsx
```

</div>

##### 2. Upsert the PDFs and metadata into the vectorstore (upsert_pdfs_and_payload.ipynb)
<div style="border: 2px solid black; padding: 10px;">

```mermaid
sequenceDiagram
    actor Curator
    participant System
    participant Vectorstore

    File Storage->>System: Retrieve latest library_catalog{}.xlsx
    System->>System: Retrieve document info from library_catalog
    System->>Vectorstore: (Weaviate only) Embed vectors, assign properties from library_catalog<BR> and add to the collection
    System->>System: Chunk PDF pages
    System->>System: Retreive page info from library_catalog
    System->>Vectorstore: Embed vectors, assign properties from library_catalog,<BR> and add to the collection
    System->>File Storage: copy PDFs to **/PDFs_library**
    System->>System: clear PDF_ingest_queue folder
```

</div>
