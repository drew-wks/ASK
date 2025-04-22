import os  # needed for local testing
import re
from datetime import datetime, timezone
from typing import List, Optional
from typing_extensions import Annotated, TypedDict
import pandas as pd 
import streamlit as st
from qdrant_client import QdrantClient
from qdrant_client.http import models  # for running filters on the metadata
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_ollama import ChatOllama  # to test other LLMs
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable  #RAG pipeline instrumentation platform
from filter_utils import build_retrieval_filter


# st.secrets pulls from ~/.streamlit when run locally

# Config Qdrant
QDRANT_URL = st.secrets["QDRANT_URL"]
QDRANT_API_KEY = st.secrets["QDRANT_API_KEY"]
QDRANT_PATH = "/Users/drew_wilkins/Drews_Files/Drew/Python/Localcode/Drews_Tools/qdrant_ASK_lib_tools/qdrant_db"  # on macOS, default is: /private/tmp/local_qdrant

# Config langchain_openai
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY_ASK"] # for langchain_openai.OpenAIEmbeddings

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY_ASK"] # for openai client in cloud environment


# Misc configs for RAG tracing in LangSmith
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
    'ASK_fetch_k': 20,   # fetch 20 docs then select 5
    'ASK_lambda_mult': .7,    # 0= max diversity, 1 is min. default is 0.5
    "ASK_score_threshold": 0.5,
    "ASK_generation_model": "gpt-4o-mini", # gpt-3.5-turbo-16k # gpt-4o-mini # gpt-4-turbo
    "ASK_temperature": 0.7,
}

#retrieval filter function is defined in filter_utils.py


# Create and cache the document retriever
#@st.cache_resource
def get_retriever(retrieval_filter: Optional[models.Filter]):
    '''Creates and caches the document retriever and Qdrant client with optional filters.'''


    # Qdrant client cloud instance
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
                       "lambda_mult": CONFIG["ASK_lambda_mult"], "filter": retrieval_filter},  # If None, no metadata filering occurs
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
        "The user is a {identity}."
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



# --- Main RAG pipeline function ---
@traceable(run_type="chain")
def rag(
    user_question: str,
    timeout: int = 60,
    filter_conditions: Optional[dict[str, str | bool | None]] = None,
    langsmith_extra: Optional[dict] = None,
) -> dict:
    "accepts user_question and an optional filter"
    
    # Run through OpenAI's chat model. This is up here becuase we sometimes use it in the retreiver too
 
    
    llm = ChatOpenAI(model=CONFIG["ASK_generation_model"], max_retries=2, timeout=45,  temperature=CONFIG["ASK_temperature"])
    
    _llm = ChatOllama(
    model="deepseek-r1:8b",  # Specify the model you want to use
    temperature=CONFIG["ASK_temperature"],  # Set the temperature parameter
    client_kwargs={
        "timeout": 50,  # Set the timeout in seconds
        # Additional client configurations can be added here if needed
    }
)
    print("\n🤖 Initiated RAG pipeline")
    # Enrich the question
    enriched_question = enrich_question(user_question)
    print("\nQuestion has been enriched")
    
    # Set the user identity
    identity = "Auxiliary member"

    # Initialize response dict
    response = {
        "answer": "⚠️ Something went wrong before answering.",
        "sources": [],
        "user_question": user_question,
        "enriched_question": enriched_question,
        "context": [],
    }
    
    # build filter (optional) and retriever
    print (f"Received filter conditions from user: \n{filter_conditions}")
    retrieval_filter = build_retrieval_filter(filter_conditions)
    print (f"\nCreated retrieval filter: \n{retrieval_filter}")
    retriever = get_retriever(retrieval_filter=retrieval_filter).with_config(metadata=CONFIG)
    
    
    # Retrieve relevant documents using the enriched question
    try:
        context = retriever.invoke(enriched_question)
        response["context"] = context
        print(f"\n📄 Retrieved context: {len(context)} documents")
        if not context:
            response["answer"] = (
                "❗️I couldn't find any documents that match your filters. Please try relaxing your filters."
            )
            return response
    except Exception as e:
        print(f"⚠️ Retriever Error: {e}")
    
    # Prepare the prompt input
    try:
        prompt = create_prompt()
        prompt_input = {
            "identity": identity,
            "enriched_question": enriched_question,
            "context": format_docs(context),  # list of documents from vectorstore
        }
        llm_response = llm.invoke(prompt.format(**prompt_input))
        response["answer"] = llm_response.content
        response["sources"] = [doc.metadata["title"] for doc in context]
        print("🧠 Received LLM response")
    except Exception as e:
        print(f"LLM Error: {e}")
        response["answer"] = f"⚠️ There was a problem generating a response: {e}",
    return response


# Adapter for running evals to LangSmith. No longer used
def rag_for_eval(input: dict) -> dict:
    # Accepts a input dict from langsmith.evaluation.LangChainStringEvaluator
    # Outputs a dictionary with one key which is the answer
    user_question = input["Question"]
    response = rag(user_question)
    return {"answer": response["answer"]}


def create_source_lists(response):
    """
    Creates and returns both the short and long source lists as strings.

    Args:
        response (dict): Contains a 'context' key with a list of document objects.

    Returns:
        tuple: (short_source_list, long_source_list) where:
            - short_source_list is a string with a markdown reference for each document.
            - long_source_list is a string with a detailed markdown reference for each document.
    """
    short_source_markdown_list = []
    long_source_markdown_list = []
    
    for i, doc in enumerate(response['context'], start=1):
        title = doc.metadata['title']
        date = doc.metadata['issue_date'][:4]
        page = str(int(doc.metadata['page']) + 1) # no page 0
        publication_number = (lambda x: (s := str(x).strip()) and s or " ")(doc.metadata.get("publication_number"))
        scope = (lambda x: " " if not x or str(x).strip().lower() == "national" else str(x).strip())(doc.metadata.get("scope"))
        unit = (lambda x: (s := str(x).strip()) and s or " ")(doc.metadata.get("unit"))
        organization = (lambda x: f"Issuer: {x.strip()}" if x and x.strip() else None)(doc.metadata.get("organization"))


        short_source_markdown_list.append(f"  *{scope} {unit} {title} [{date}], page {page}\n  ")
        
        page_content = doc.page_content  
        long_source_markdown_list.append(
            f"**Reference {i}:**  \n    {scope} {unit} {title} [{date}], page {page}  \n  {publication_number}  \n  {organization}\n   {scope} {unit}\n\n  "
            f"{page_content}\n\n  "
            f"***  "
        )
    
    short_source_list = '\n'.join(short_source_markdown_list)
    long_source_list = '  \n'.join(long_source_markdown_list)
    
    return short_source_list, long_source_list

