#### ASK Feature Roadmap
Planned improvements for ASK over the coming months  


##### Speed and Accuracy: continue to improve the results
[x] Explore better prompts through prompt templates   
[x] Tune retrieval hyperparameters such as lambda, k-means 
[x] Tag documents with effective date  
[x] Insert a pre-prompting/inference step to ensure all relevant docs are retrieved
[ ] Incorporate search filtering (hybrid search) capability, possible via sparce vectors
[ ] Test search filtering Include effective date in retrieval and explore giving greater to weight to more recent documents: currently assessing 
[ ] Test new document pre-processing approaches that can preseve semantic meaning contained in its hierarchical structure (e.g., unstructured.io)
[ ] Test new document pre-processing approaches that can parse table and image info
[ ] Reason through contradictions in corpus docs (e.g., conflicting policies)
[ ] Test other private and [open-source embedding models](https://huggingface.co/spaces/mteb/leaderboard) incl. cohere, anarchy  


##### Evaluation & Observability: tooling to measure and assess performance  
[x] Select instrumentation provider: wandb, Neptune, Trubrics    
[x] Implement Trubrics for logging prompts and human feedback
[ ] Evaluate Neptune platform for incorporating [RAG quality metrics](https://docs.rungalileo.io/galileo/gen-ai-studio-products/galileo-guardrail-metrics#rag-quality-metrics) 
[ ] Add tokens usage and RAG query parameters to Truberics logs


##### Administration: simplify backend through automation  
[x] Evaluate Vectara db  
[x] Scheduled checks of Qdrant and Streamlit for health via Github Actions
[x] Enable direct export of Library List Report from Qdrant into UI via xlsx  
[x] Check duplicate PDFs feature directly at the vector db "source of truth" 
[x] Review, modify, delete documents directly at the vector db  
[x] Remove PDFs- acheived via langchain.vectorstores.qdrant.Qdrant.delete([vector IDs])  
[x] Evaluate Ray for ASK 
[ ] Explore alternative database such as Weaviate that can separate doc level info and page level info into separate collections
[ ] Explore model-based metadata extraction using unstructured


##### UI Enhancements: making ASK easier and more enjoyable to use  
[x] Implement workaround chat input field on mobile devices (a bug with streamlit)  
[x] Bring feedback back into the UI  
[x] Get Streamlit working faster via st.session_state and st.cache_resource
[x] Incorporate better visual status into UI  
[x] Add a warning when the underlying LLM (e.g., OpenAI) is down  


##### Code and Platform Simplification: make ASK easier to maintain and extend
[ ] Use LangChain's prompt templates with dynamic enrichment rather than manually parsing Excel files.
