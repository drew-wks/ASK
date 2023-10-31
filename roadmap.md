# ASK Feature Roadmap
These are some of the the things I plan to do over the coming months to continue to improve ASK

## Library (Corpus) Management 
- Report and administrate directly at the vector db "source of truth"
    - Direct export of Library List Report into UI
    - Modify metadata in payload via streamlit
    - Check duplicate PDFs
    - Remove PDFs
- Evaluate Ray for ASK

## Inference  
- Identify contraditions in policy, notify user, and give more recent docunents greater weight in response
- Explore better prompts through prompt templates
- Test other commercial and ([open-source embedding models](https://huggingface.co/spaces/mteb/leaderboard)

## UI Enhancements  
- Implement workaround chat input field on mobile devices (a bug with streamlit)
- Bring feedback back into the UI
- Incorporate better visual status into UI

## Instrumentation  
- Add tokens used to truberics
- Add parameters to trubrics feed
- Explore IP address gathering on Streamlit cloud

## Speed and Accuracy  
- Remove superfluous metadata from chunks
- Explore other chunking strategies
- st.session_state

## Process Automation  
- Utilize agents to replace programmatic work such as bringing metadata into chunks
- Explore having agent extract doc purpose and incoporate as metadata

## Leapfrogging
### Explore new frameworks and paltforms to simplify/improve our solution
- Evaluate Vectara
