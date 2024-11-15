import os
import pandas as pd
import re
from typing import List
from typing_extensions import Annotated, TypedDict
import streamlit as st
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


# Config LangSmith
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "ASK_main"

# Config Qdrant
QDRANT_URL = st.secrets["QDRANT_URL"]
QDRANT_API_KEY = st.secrets["QDRANT_API_KEY"]
qdrant_path = "/tmp/local_qdrant"

# Config langchain_openai
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"] # for langchain_openai.OpenAIEmbeddings

# Misc configs for tracing
CONFIG = {
    "qdrant_collection_name": "ASK_vectorstore",
    "embedding_model": "text-embedding-ada-002", # alt: text-embedding-3-large
    "embedding_dims": 1536, # alt: 1024
    "search_type": "mmr",
    "k": 5,
    'fetch_k': 20,   # fetch 30 docs then select 5
    'lambda_mult': .7,    # 0= max diversity, 1 is min. default is 0.5
    "score_threshold": 0.5,
    "generation_model": "gpt-3.5-turbo-16k",
    "temperature": 0.7,
}


# keep outside the function so it's accessible elsewhere in this notebook
llm = ChatOpenAI(model=CONFIG["generation_model"], temperature=CONFIG["temperature"])


# Create and cache the document retriever
@st.cache_resource
def get_retriever():
    '''Creates and caches the document retriever and Qdrant client.'''

    # Qdnrat client cloud instance.
    client = QdrantClient(
        url=QDRANT_URL,
        prefer_grpc=True,
        api_key=QDRANT_API_KEY,
    )  # For local, use QdrantClient(path="/tmp/local_qdrant")  # on mac: /private/tmp/local_qdrant

    qdrant = QdrantVectorStore(
        client=client,
        collection_name=CONFIG["qdrant_collection_name"],
        embedding=OpenAIEmbeddings(model=CONFIG["embedding_model"]),
    )

    retriever = qdrant.as_retriever(
        search_type=CONFIG["search_type"],
        search_kwargs={'k': CONFIG["k"], "fetch_k": CONFIG["fetch_k"],
                       "lambda_mult": CONFIG["lambda_mult"], "filter": None},  # filter documents by metadata
    )

    return retriever



# Define schema for response
class AnswerWithSources(TypedDict):
    """An answer to the question, with sources."""
    answer: str
    sources: Annotated[
        List[str],
        ...,
        "List of sources and pages used to answer the question",
    ]


# Cache data retrieval function
#@st.cache_data
def get_retrieval_context(file_path: str):
    '''Reads the worksheets Excel file into a dictionary of dictionaries.'''
    xls = pd.ExcelFile(file_path)
    context_dict = {}
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        if df.shape[1] >= 2:
            context_dict[sheet_name] = pd.Series(
                df.iloc[:, 1].values, index=df.iloc[:, 0]).to_dict()
    return context_dict


# Cache the prompt template
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
        ("human", "{input}"),
    ])

# Path to prompt enrichment dictionaries
config_path = os.path.join(os.path.dirname(__file__), 'config/retrieval_context.xlsx')


# Define and cache the enrichment function to use cached context
#@st.cache_data
def enrich_question_via_code(user_question: str, filepath=config_path) -> str:
    retrieval_context_dict = get_retrieval_context(filepath)
    acronyms_dict = retrieval_context_dict.get("acronyms", {})
    terms_dict = retrieval_context_dict.get("terms", {})

    enriched_question = user_question
    for acronym, full_form in acronyms_dict.items():
        if pd.notna(acronym) and pd.notna(full_form):
            enriched_question = re.sub(
                r'\b' + re.escape(str(acronym)) + r'\b', str(full_form), enriched_question)
    for term, explanation in terms_dict.items():
        if pd.notna(term) and pd.notna(explanation):
            if str(term) in enriched_question:
                enriched_question += f" ({str(explanation)})"
    return enriched_question


# Function to format documents (doesn't require caching)
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# Define and cache the RAG pipeline setup
# @st.cache_resource
def create_rag_pipeline():
    prompt = create_prompt()
    rag_chain_from_docs = (
        {
            "input": lambda x: x["input"],
            "context": lambda x: format_docs(x["context"]),
        }
        | prompt
        | llm.with_structured_output(AnswerWithSources)
    )
    retrieve_docs = (lambda x: x["input"]) | get_retriever().with_config(metadata=CONFIG)
    return RunnablePassthrough.assign(context=retrieve_docs).assign(answer=rag_chain_from_docs)


# Define the RAG pipeline
def rag(user_question):
    chain = create_rag_pipeline()
    enriched_question = enrich_question_via_code(user_question)
    response = chain.invoke({"input": enriched_question})

    # Response as LangChain Document object and enriched question
    return response, enriched_question

# Extract short source list from response
def create_short_source_list(response):
    markdown_list = []
    
    for i, doc in enumerate(response['context'], start=1):
        page_content = doc.page_content
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



if __name__ == "__main__":
    # Example code to test the RAG pipeline directly
    print("Starting RAG pipeline test")
    
    # Sample test question
    user_question = "What are the requirements for boat crew certification?"
    
    # Run the RAG pipeline and get a response
    response, enriched_question = rag(user_question)
    
    # Display the results
    print("Enriched Question:", enriched_question)
    print("Response:", response)
