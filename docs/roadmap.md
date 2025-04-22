#### ASK Feature Roadmap
Planned improvements for ASK. Submit your requests on the Feedback page  
###### 
##### Speed and Accuracy: continue to improve the results
[ ] Test new document pre-processing approaches that can parse table and image info  
[ ] Reason through contradictions in corpus docs (e.g., conflicting policies)  
[ ] Test other private and [open-source embedding models](https://huggingface.co/spaces/mteb/leaderboard) incl. cohere, anarchy  
[X] Incorporate search filtering (hybrid search) capability, possible via sparce vectors  
[ ] Test search filtering Include effective date in retrieval and explore giving greater to weight to more recent documents: currently assessing   
[x] Switch from GPT 3.5 to o1 for retrieval  
[x] Test new document pre-processing approaches that can preseve semantic meaning contained in its hierarchical structure (e.g., unstructured.io open source lib)  
[x] Evaluted Deepseek-r1 for inference  
[x] Explore better prompts through prompt templates   
[x] Tune retrieval hyperparameters such as lambda, k-means  
[x] Tag documents with effective date  
[x] Insert a pre-prompting/inference step to ensure all relevant docs are retrieved  


##### Evaluation & Observability: tooling to measure and assess performance  
[x] Migrated to Langsmith for observability and evaluation. Built out RAG metrics and eval set  
[x] Evaluated pytest evaluation package. Too complicated and quite limited  
[x] Evaluted instrumentation providers: wandb, Neptune, Trubrics, Langsmith    
[x] Implement Trubrics for logging prompts and human feedback  
[ ] Evaluate Neptune platform for incorporating [RAG quality metrics](https://docs.rungalileo.io/galileo/gen-ai-studio-products/galileo-guardrail-metrics#rag-quality-metrics)  


##### Administration: simplify backend through automation  
[x] Separated library admin repo from RAG repo for ease of maintenance and testing  
[x] Created automated tasks for Streamlit UI and Qdrant vector db check using Github Actions  
[x] Scheduled checks of Qdrant and Streamlit for health via Github Actions  
[x] Enable direct export of Library List Report from Qdrant into UI via xlsx    
[x] Check duplicate PDFs feature directly at the vector db "source of truth"  
[x] Review, modify, delete documents directly at the vector db  
[x] Remove PDFs- acheived via langchain.vectorstores.qdrant.Qdrant.delete([vector IDs])  
[x] Evaluate Ray for ASK  
[x] Explore alternative database such as Weaviate that can separate doc level info and page level info into separate collections  
[ ] Explore model-based metadata extraction using unstructured


##### UI Enhancements: making ASK easier and more enjoyable to use  
[x] Improved document citations to include document title and issue date  
[x] Implement workaround chat input field on mobile devices (a bug with streamlit)  
[x] Bring feedback back into the UI  
[x] Get Streamlit working faster via st.session_state and st.cache_resource  
[x] Incorporate better visual status into UI  
[x] Add a warning when the underlying LLM (e.g., OpenAI) is down  


##### Code and Platform Simplification: make ASK easier to maintain and extend
[ ] Use LangChain's prompt templates with dynamic enrichment rather than manually parsing Excel files.
