# ASK Feature Roadmap
These are some of the the things I plan to do over the coming months to continue to improve ASK

## Library (Corpus) Management 
- Report and administrate directly at the vector db "source of truth"
    - [x] Direct export of Library List Report into UI
    - Modify metadata in payload via streamlit
    - Check duplicate PDFs
    - Remove PDFs- acheived via langchain.vectorstores.qdrant>Qdrant.delete([vector IDs])
- Evaluate Ray for ASK

## Inference  
- Reason through contractitions in corpus docs (e.g., conflicting policies)
    -[x] Tag documents with effective date
    - Include effective date in retrieval 
    - Give greater to weight to more recent documents
- Explore better prompts through prompt templates
- Test other private and [open-source embedding models](https://huggingface.co/spaces/mteb/leaderboard)

## UI Enhancements  
- Implement workaround chat input field on mobile devices (a bug with streamlit)
- Bring feedback back into the UI
- Incorporate better visual status into UI

## Instrumentation  
- [x] Assess instrumentation providers: wandb, neptune, Trubrics
- Continue to build out on Truberics
    - Add tokens usage to truberics
    - Add parameters to trubrics feed
    - Explore IP address gathering on Streamlit cloud
- Explore Neptune platform

## Speed and Accuracy  
- Remove superfluous metadata from chunks
- Explore other chunking strategies
- Get Strealit working faster via st.session_state and st.database

## Process Automation  
- Utilize agents to replace programmatic work such as bringing metadata into chunks
- Explore having agent extract doc purpose and incoporate as metadata

## Leapfrogging
### Explore new frameworks and paltforms to simplify/improve our solution
- [x] Evaluate Vectara