#### ASK Feature Roadmap
These are some of the the things I plan to do over the coming months to continue to improve ASK

##### Library Management: these are the documents ASK uses to provide responses 
- [ ] Report and administrate directly at the vector db "source of truth"
    - [x] Direct export of Library List Report from Qdrant into UI via xlsx
    - [x] Check duplicate PDFs
    - [ ] Modify metadata in payload via streamlit
    - [x] Remove PDFs- acheived via langchain.vectorstores.qdrant.Qdrant.delete([vector IDs])
- [x] Evaluate Ray for ASK

##### Inference: this is the process of generating a response from the documents  
- [ ] Reason through contractitions in corpus docs (e.g., conflicting policies)
    - [x] Tag documents with effective date
    - [ ] Index additional metadata
    - [ ] Include effective date in retrieval 
    - [ ] Give greater to weight to more recent documents
- [x] Explore better prompts through prompt templates
- Test other private and [open-source embedding models](https://huggingface.co/spaces/mteb/leaderboard) incl. cohere, anarchy

###### UI Enhancements: making ASK easier to use  
- [x] Implement workaround chat input field on mobile devices (a bug with streamlit)
- [x] Bring feedback back into the UI
- [x] Incorporate better visual status into UI

##### Instrumentation: tooling to measure and assess performance  
- [x] Assess instrumentation providers: wandb, neptune, Trubrics
- [ ] Continue to build out on Truberics
    - [ ] Add tokens usage to truberics
    - [ ] Add parameters to trubrics feed
    - [ ] Explore IP address gathering on Streamlit cloud
- [ ] Explore Neptune platform

##### Speed and Accuracy  
- [ ] Remove superfluous metadata from chunks
- [ ] Explore other chunking strategies
- [ ] Get Strealit working faster via st.session_state and st.database

##### Leapfrogging everything with Game Changers
- Enhance features and simplify backend through automation
    - [x] Evaluate Vectara
    - [ ] Utilize agents to replace programmatic work such as bringing metadata into chunks
    - [ ] Explore having agent extract doc purpose and incoporate as metadata
