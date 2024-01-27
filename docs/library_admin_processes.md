## ASK System Administration (Weaviate)
#### Adding PDFs to Library
##### 1. Prepare the document metadata

```mermaid
sequenceDiagram
    actor Curator
    participant System
    participant John
    Curator->>System: specify target PDFs to add
    create participant FileStorage
    System->>FileStorage: copy PDFs to PDF_ingest_queue folder
    John-->>Curator: Great!
    John->>System: How about you?
    System-->>John: Jolly good!
```
