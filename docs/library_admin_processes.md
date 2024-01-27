## ASK System Administration (Weaviate)
#### Adding PDFs to Library
##### 1. Prepare the document metadata

```mermaid
sequenceDiagram
    actor Curator
    participant System
    participant File Storage
    Curator->>System: specify target PDFs to add
    create participant File Storage
    System->>File Storage: copy PDFs to PDF_ingest_queue folder
    John-->>Curator: Great!
    John->>System: How about you?
    System-->>John: Jolly good!
```
