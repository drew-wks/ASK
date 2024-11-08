# %% [markdown]
# Assumes Langchain v.0.3.4
# 

# %%
# %pip install --upgrade --quiet langchain-openai
# %pip install langchain-qdrant
# % pip install streamlit

# %%
import streamlit as st
import pandas as pd
import re

# %% [markdown]
# ### Langsmith
# accessible [here](https://smith.langchain.com/o/3941ecea-6957-508c-9f4f-08ed62dc7d61/projects/p/0aea481f-080e-45eb-bae1-2ae8ee246bd9)

# %%
# LANGSMITH CONFIG
#
# These have to be set as environmental variables to be accessed behind the scenes
import os
from dotenv import load_dotenv, find_dotenv

env_path = find_dotenv()
load_dotenv(env_path)

# os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["LANGCHAIN_TRACING_V2"]
# os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]

os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "ASK_main"

# %%
# required for langchain_openai.OpenAIEmbeddings
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
# open_api_key = st.secrets["OPENAI_API_KEY"]

# %%
from qdrant_client import QdrantClient
# from langchain.vectorstores import Qdrant Deprecated
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

# %%
config = {
    # langchain. No longer needs the API key parameter in 0.3.4
    # install ``langchain_openai`` and set``OPENAI_API_KEY`
    "embedding": OpenAIEmbeddings(),
    "embedding_dims": 1536,
    "search_type": "mmr",
    "k": 5,
    'fetch_k': 20,   # fetch 30 docs then select 4
    'lambda_mult': .7,    # 0= max diversity, 1 is min. default is 0.5
    "score_threshold": 0.5,
    "model": "gpt-3.5-turbo-16k",
    "temperature": 0.7,
    "chain_type": "stuff",  # a LangChain parameter
}

qdrant_collection_name = "ASK_vectorstore"
qdrant_path = "/tmp/local_qdrant"

# %%
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import List
from langchain_core.runnables import RunnablePassthrough
from typing_extensions import Annotated, TypedDict

# keep outside the function so it's accessible elsewhere in this notebook
llm = ChatOpenAI(model=config["model"], temperature=config["temperature"])
query = []

# %%
@st.cache_resource
def get_retriever():
    '''Creates and caches the document retriever and Qdrant client.'''

    client = QdrantClient(
        url=st.secrets["QDRANT_URL"],
        prefer_grpc=True,
        api_key=st.secrets["QDRANT_API_KEY"]
    )  # cloud instance
    # client = QdrantClient(path="/tmp/local_qdrant" )  # local instance: /private/tmp/local_qdrant

# Qdrant is deprecated. Use this instead. Notice embedding is singular
    qdrant = QdrantVectorStore(
        client=client,
        collection_name=qdrant_collection_name,
        embedding=config["embedding"]
    )

    retriever = qdrant.as_retriever(
        search_type=config["search_type"],
        search_kwargs={'k': config["k"], "fetch_k": config["fetch_k"],
                       "lambda_mult": config["lambda_mult"], "filter": None},  # filter documents by metadata
    )

    return retriever

# %% [markdown]
# ## 3. Create your optional user question enrichment

# %%
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
@st.cache_data
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


# Cache the prompt creation
@st.cache_resource
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


# Cache enrichment function to use cached context
@st.cache_data
def enrich_question_via_code(user_question: str) -> str:
    retrieval_context_dict = get_retrieval_context(
        'config/retrieval_context.xlsx')
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


# Caching the RAG pipeline setup as a resource
@st.cache_resource
def create_rag_pipeline():
    prompt = create_prompt()
    rag_chain_from_docs = (
        {
            "input": lambda x: enrich_question_via_code(x["input"]),
            "context": lambda x: format_docs(x["context"]),
        }
        | prompt
        | llm.with_structured_output(AnswerWithSources)
    )
    retrieve_docs = (lambda x: x["input"]) | get_retriever()
    return RunnablePassthrough.assign(context=retrieve_docs).assign(answer=rag_chain_from_docs)


# RAG invocation
def rag(user_question):
    chain = create_rag_pipeline()
    response = chain.invoke({"input": user_question})
    return response


user_question = "what is required to wear the VE insignia?"
response = rag(user_question)
response

# %%


# %% [markdown]
# ## 3. Create the pipeline using LCEL

# %% [markdown]
# ### Custom LCEL implementation which allows you the option of only returning sources that were actually used in the response
# 

# %% [markdown]
# It works by building up a dict with the input query,
# then add the retrieved docs in the `"context"` key;
# Feed both the query and context into a RAG chain and add the result to the dict.
# 
# We use the model's tool-calling features to generate structured output, consisting of an answer and list of sources. The schema for the response is represented in the `AnswerWithSources` TypedDict, below.
# We remove the `StrOutputParser()`, as we expect `dict` output in this scenario.
# Note that `result` is a dict with keys `"input"`, `"context"`, and `"answer"`:
# 

# %%




# %% [markdown]
# THis outputs the model's response as well as the subset of retrieved information that it used to infer its response.
# 
# Note that the `answer` element in the `response` disctionary is itself a dictionary containing `answer` and `source` keys
# 

# %% [markdown]
# ## 4. Run the RAG

# %%
'''
user_question = "How long can someone be VNACO in the Auxiliary?"
user_question = enrich_question_via_code(user_question)
retriever = get_retriever()
response = chain.invoke({"input": user_question})
'''

# %%
response

# %%
response = chain.invoke(
    {"input": user_question})
response

# %%
import json

print(json.dumps(response["answer"], indent=2))

# %% [markdown]
# ### Since the response object also contains-- the original query, all the retrieved docs, the LLM response, and the sources used by the model to generate its answer-- we can also list the titles of the retrieved documents and the source page content
# 

# %%
'''
    item.page_content
    item.metadata['source']
    item.metadata['page']
'''
print("Sources:")
for item in response["context"]:
    print(
        f"{item.metadata['source']} page {item.metadata['page']}" + "\n")

# %% [markdown]
# ### THis one is formatted in the same way as the short source list in ASK
# 

# %%
markdown_list = []

for i, doc in enumerate(response['context'], start=1):
    page_content = doc.page_content
    source = doc.metadata['source']
    short_source = source.split('/')[-1].split('.')[0]
    page = doc.metadata['page']
    markdown_list.append(f"*{short_source}*, page {page}\n")

short_source_list = '\n'.join(markdown_list)
print(short_source_list)

# %% [markdown]
# ### THis one is formatted in the same way as the long source list in ASK
# 

# %%
markdown_list = []

for i, doc in enumerate(response['context'], start=1):
    page_content = doc.page_content
    source = doc.metadata['source']
    short_source = source.split('/')[-1].split('.')[0]
    page = doc.metadata['page']
    markdown_list.append(
        f"**Reference {i}:**    *{short_source}*, page {page}   {page_content}\n")

long_source_list = '\n'.join(markdown_list)
print(long_source_list)

# %% [markdown]
# ### For reference, here's the full response object. You can see it contains the original query all the retrieved docs, the LLM response, and the sources used by the model to generate its answer.
# 

# %%
import json

print(json.dumps(response, indent=2, default=str))

# %%



