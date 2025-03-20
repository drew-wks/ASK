import os
import pandas as pd
import re
from typing import List
from typing_extensions import Annotated, TypedDict
import streamlit as st
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable
from langchain.retrievers.document_compressors import LLMChainExtractor



# Config Qdrant
QDRANT_URL = st.secrets["QDRANT_URL"]
QDRANT_API_KEY = st.secrets["QDRANT_API_KEY"]
QDRANT_PATH = "/Users/drew_wilkins/Drews_Files/Drew/Python/Localcode/Drews_Tools/qdrant_ASK_lib_tools/qdrant_db"  # on macOS, default is: /private/tmp/local_qdrant

# Config langchain_openai
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"] # for langchain_openai.OpenAIEmbeddings


# Misc configs for tracing
CONFIG = {
    "qdrant_collection_name": "ASK_vectorstore",
    "embedding_model": "text-embedding-ada-002", # alt: text-embedding-3-large
    "ASK_embedding_dims": 1536, # alt: 1024
    "splitter_type": "pypdf",
    "chunk_size": 2000,
    "chunking_strategy": "by_page",
    "ASK_retriever_type": "Standard", # ContextualCompressionRetriever
    "ASK_search_type": "mmr",
    "ASK_k": 5,
    'ASK_fetch_k': 20,   # fetch 30 docs then select 5
    'ASK_lambda_mult': .7,    # 0= max diversity, 1 is min. default is 0.5
    "ASK_score_threshold": 0.5,
    "ASK_generation_model": "gpt-4o-mini", # gpt-3.5-turbo-16k # gpt-4o-mini # gpt-4-turbo
    "ASK_temperature": 0.7,
}

CONFIG_UNSTRUCTURED = {
    "splitter_type": "unstructured.partition",
    "chunk_size": 4000,
    "chunking_strategy": "by_title",
    "qdrant_collection_name": "ASK_vectorstore-oai-ada-002-unstructured-os", #
    "embedding_model": "text-embedding-ada-002",  # alt: text-embedding-3-large
    "ASK_embedding_dims": 1536,  # alt: 1024
    "vector_name": "text-dense",
    "sparse_vector_name": "None",
    "sparse_embedding": "None",
    "ASK_retriever_type": "Standard",
    "ASK_search_type": "mmr",
    "ASK_k": 5,
    'ASK_fetch_k': 20,   # fetch 30 docs then select 5
    'ASK_lambda_mult': .7,    # 0= max diversity, 1 is min. default is 0.5
    "ASK_score_threshold": 0.5,
    "ASK_generation_model": "gpt-4o-mini",
    "ASK_temperature": 0.7,
}


# Create and cache the document retriever
@st.cache_resource
def get_retriever():
    '''Creates and caches the document retriever and Qdrant client.'''

    # Qdnrat client cloud instance
    client = QdrantClient(
        url=QDRANT_URL,
        prefer_grpc=True,
        api_key=QDRANT_API_KEY,
        # path=QDRANT_PATH  # local instance
    )  

    qdrant = QdrantVectorStore(
        client=client,
        collection_name=CONFIG["qdrant_collection_name"],
        embedding=OpenAIEmbeddings(model=CONFIG["embedding_model"]),
    )

    retriever = qdrant.as_retriever(
        search_type=CONFIG["ASK_search_type"],
        search_kwargs={'k': CONFIG["ASK_k"], "fetch_k": CONFIG["ASK_fetch_k"],
                       "lambda_mult": CONFIG["ASK_lambda_mult"], "filter": None},  # filter documents by metadata
    )

    return retriever



# Cache data retrieval function
#@st.cache_data
def get_retrieval_context(file_path: str):
    '''Reads the worksheets Excel file into a dictionary of dictionaries.'''
    context_dict = {}
    for sheet_name in pd.ExcelFile(file_path).sheet_names:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        if df.shape[1] >= 2:
            context_dict[sheet_name] = pd.Series(
                df.iloc[:, 1].values, index=df.iloc[:, 0]).to_dict()
    return context_dict



# Path to prompt enrichment dictionaries
enrichment_path = os.path.join(os.path.dirname(__file__), 'config/retrieval_context.xlsx')


# Define the enrichment function.
# traceable decorator is used to trace the function in Langsmith
# cache_data decorator is used to cache the function in Streamlit
@traceable(run_type="prompt")
#@st.cache_data
def enrich_question(user_question: str, filepath=enrichment_path) -> str:
    enrichment_dict = get_retrieval_context(filepath)
    acronyms_dict = enrichment_dict.get("acronyms", {})
    terms_dict = enrichment_dict.get("terms", {})

    enriched_question = user_question
    # Replace acronyms with full form
    for acronym, full_form in acronyms_dict.items():
        if pd.notna(acronym) and pd.notna(full_form):
            enriched_question = re.sub(
                r'\b' + re.escape(str(acronym)) + r'\b', str(full_form), enriched_question)
    # Add explanations
    for term, explanation in terms_dict.items():
        if pd.notna(term) and pd.notna(explanation):
            if str(term) in enriched_question:
                enriched_question += f" ({str(explanation)})"
    return enriched_question



def create_prompt():
    system_prompt = (
        "Use the following pieces of context to answer the users question. "
        "INCLUDES ALL OF THE DETAILS IN YOUR RESPONSE, INDLUDING REQUIREMENTS AND REGULATIONS. "
        "National Workshops are required for boat crew, aviation, and telecommunications when they are offered. "
        "Include Auxiliary Core Training (AUXCT) for questions on certifications or officer positions. "
        "If you don't know the answer, just say I don't know. \n----------------\n{context}"
    )
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{enriched_question}"),
    ])



# Function to format documents (doesn't require caching)
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)



# Schema for llm responses
class AnswerWithSources(TypedDict):
    """An answer to the question, with sources."""
    answer: str
    sources: Annotated[
        List[str],
        ...,
        "List of sources and pages used to answer the question",
    ]



# Main RAG pipeline function
@traceable(run_type="chain")
def rag(user_question: str, timeout: int = 60) -> dict:
    
    # Run through OpenAI's chat model. This is up here becuase we sometimes use it in the retreiver too
    llm = ChatOpenAI(model=CONFIG["ASK_generation_model"], max_retries=2, timeout=45,  temperature=CONFIG["ASK_temperature"])
    
    ollama_llm = ChatOllama(
    model="deepseek-r1:8b",  # Specify the model you want to use
    temperature=CONFIG["ASK_temperature"],  # Set the temperature parameter
    client_kwargs={
        "timeout": 50,  # Set the timeout in seconds
        # Additional client configurations can be added here if needed
    }
)

    # Enrich the question
    enriched_question = enrich_question(user_question)

    # Initialize a document retriever
    retriever = get_retriever().with_config(metadata=CONFIG)

    
    # Retrieve relevant documents using the enriched question
    try:
        # Retrieve relevant documents using the enriched question
        context = retriever.invoke(enriched_question)
        print(f"Retrieved context: {len(context)} documents.")
    except Exception as e:
        print(f"Retriever Error: {e}")
        context = []
    
    if context:
        try:
            # Prepare the prompt input
            prompt = create_prompt()
            prompt_input = {
                "enriched_question": enriched_question,
                "context": format_docs(context),  # list of documents retreived from vector store
            }
            # Structure output with AnswerWithSources custom parser to include the sources used by LLM
            structured_llm = llm.with_structured_output(AnswerWithSources)
            llm_response = llm.invoke(prompt.format(**prompt_input))
            print("LLM response received")
        except Exception as e:
            print(f"LLM Error: {e}")


    return {
        "answer": llm_response.content,
        # "answer": llm_response["answer"], # used for the old AnswerWithSources
        "sources": [doc.metadata['title'] for doc in context],
        "user_question": user_question,
        "enriched_question": enriched_question,
        "context": context,  
        # "llm_sources": llm_response.get("sources", ["No sources returned by LLM"])
    }


# Specialized adapter for running evals to LangSmith. No longer used
def rag_for_eval(input: dict) -> dict:
    # Accepts a input dict from langsmith.evaluation.LangChainStringEvaluator
    # Outputs a dictionary with one key which is the answer
    user_question = input["Question"]
    response = rag(user_question)
    return {"answer": response["answer"]}



# Extract short source list from response
def create_short_source_list(response):
    markdown_list = []

    for i, doc in enumerate(response['context'], start=1):
        source = doc.metadata['source']
        short_source = source.split('/')[-1].split('.')[0]
        page = doc.metadata['page']
        markdown_list.append(f"*{short_source}*, page {page}\n")

    short_source_list = '\n'.join(markdown_list)

    return short_source_list


# Extract long source list from response
def create_long_source_list(response):
    markdown_list = []

    for i, doc in enumerate(response['context'], start=1):
        page_content = doc.page_content  
        source = doc.metadata['source']  
        short_source = source.split('/')[-1].split('.')[0]  
        page = doc.metadata['page']  
        markdown_list.append(f"**Reference {i}:**    *{short_source}*, page {page}  \n   {page_content}\n")

    long_source_list = '\n'.join(markdown_list)

    return long_source_list
