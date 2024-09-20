
import pickle
import json
from langchain.chat_models import ChatOpenAI
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant
from langchain.chains import RetrievalQA, StuffDocumentsChain, LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import tiktoken
import streamlit as st
import openai
import pandas as pd
import utils


'''
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
'''

from langchain.embeddings import OpenAIEmbeddings

config = {
    "embedding": OpenAIEmbeddings(),  # includes a pull of the open api key
    "embedding_dims": 1536,
    "search_type": "mmr",
    "k": 5,
    'fetch_k': 20,   # fetch 30 docs then select 4
    'lambda_mult': .7,    # 0= max diversity, 1 is min. default is 0.5
    "score_threshold": 0.5,
    "model": "gpt-3.5-turbo-16k",
    "temperature": 0.7,
    "chain_type": "stuff", # a LangChain parameter
}

qdrant_collection_name = "ASK_vectorstore"
qdrant_path = "/tmp/local_qdrant" # Only required for local instance /private/tmp/local_qdrant
openai.api_key = st.secrets["OPENAI_API_KEY"] # Use this version for streamlit
llm=ChatOpenAI(model=config["model"], temperature=config["temperature"]) #keep outside the function so it's accessible elsewhere in this notebook


query = []

# Initialize the vector database and langchain clients

def qdrant_connect_local():
    print("attempting to assign qdrant local client")
    
    if 'client' in globals():
        print(f"found a global qdrant client has been assigned")
        return globals()['client']  # Return the existing client
    client = QdrantClient(path=qdrant_path)  # Only required for a local instance
    return client


def qdrant_connect_cloud(api_key, url):
    print("attempting to assign qdrant cloud client")
    
    if 'client' in globals():
        print(f"found a global qdrant client has been assigned")
        return globals()['client']  # Return the existing client
    client = QdrantClient(
        url=url, 
        prefer_grpc=True,
        api_key=api_key,
    )
    return client


def create_langchain_qdrant(client):
    '''create a langchain vectorstore object'''
    qdrant = Qdrant(
        client=client, 
        collection_name=qdrant_collection_name, 
        embeddings=config["embedding"]
    )
    return qdrant


def init_retriever_and_generator(qdrant):
    '''initialize a document retriever and response generator'''
    retriever = qdrant.as_retriever(
        search_type=config["search_type"], 
        search_kwargs={'k': config["k"], "fetch_k": config["fetch_k"], "lambda_mult": config["lambda_mult"], "filter": None}, # filter documents by metadata
    )
    return retriever


try:
    # Cache the Qdrant client connection for performance optimization
    qdrant_connect_cloud_cached = st.cache_resource(qdrant_connect_cloud)
    api_key = st.secrets.QDRANT_API_KEY
    url = st.secrets.QDRANT_URL
    client = qdrant_connect_cloud_cached(api_key, url) # alt qdrant_connect_cloud to see changes
    qdrant = create_langchain_qdrant(client)
    retriever = init_retriever_and_generator(qdrant)
except Exception as e:
    st.error(f"An error occurred while setting up the Qdrant client: {e}")
    st.stop() 



def retrieval_context_excel_to_dict(file_path):
    ''' 
    Reads an Excel file into a dictionary of dictionaries. 

    Each worksheet is read as its own dictionary, where 
    the values in the first column are the keys and the 
    values in the second column are the values. If a 
    worksheet has fewer than two columns, it will be skipped.
    
    Args:
        file_path (str): The path to the Excel file.

    Returns:
        dict: A dictionary where each key is a sheet name, 
        and the value is a dictionary with key-value pairs 
        from the first two columns of the worksheet.
    '''


    xls = pd.ExcelFile(file_path)
    dict = {}

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        if df.shape[1] >= 2:
            dict[sheet_name] = pd.Series(
                df.iloc[:, 1].values, index=df.iloc[:, 0]).to_dict()
        else:
            print(f"The sheet '{sheet_name}' does not have enough columns.")
    return dict



def query_maker(user_question):
    '''Modifies the user's question by adding context from acronym definitions and jargon explanations.

    This function retrieves two dictionaries, 'acronyms' and 'terms', from an Excel file and uses them to modify the user's question.
    
    - The 'acronyms' dictionary maps acronyms to their full definitions, which are used to replace acronyms in the question.
    - The 'terms' dictionary provides additional information for specific terms or jargon, which are appended to the user's question when those terms are identified.

    The Excel file containing the 'acronyms' and 'terms' dictionaries is parsed by the 'retrieval_context_excel_to_dict' function, which processes the file and converts relevant sheets into dictionaries.
    '''

    retrieval_context_dict = retrieval_context_excel_to_dict('config/retrieval_context.xlsx')
    acronyms_dict = retrieval_context_dict.get("acronyms", None)
    acronyms_json = json.dumps(acronyms_dict, indent=4)
    terms_dict = retrieval_context_dict.get("terms", None)
    terms_json = json.dumps(terms_dict, indent=4)

    system_message = """
    Your task is to modify the user's question based on two lists: 'acronym_json' and 'terms_json'. Each list contains terms and their associated additional information. Follow these instructions:

    - Review the user's question and identify if any acronyms from 'acronym_json' or phrases in 'terms_json' appear in it.
    - If an acronym from 'acronym_json' replace the term with the associated additional information.
    - If a phrase from 'terms_json' appears in the question, append its associated additional information to the end of the question.
    - Do not remove or alter any other part of the original question.
    - Do not provide an answer to the question.
    - If no terms from either list are found in the question, leave the question as is.

    Example:
    - Question: How do I get a VE certification?
    - Your response: How do I get a vessel examiner certification? Certification includes information about initial qualification.

    - Question: What are the requirements for pilot training?
    - Your response: What are the requirements for pilot training? Pilot is a position in the aviation program.

        - Question: What is required to stay current in the Auxiliary?
    - Your response: What is required to stay current in the Auxiliary? To be in the Auxiliary, members are required to maintain the Core Training (AUXCT), undego an annual uniform inspection, and pay annual dues.
    """

    user_message = f"User question: {user_question}```acronyms_json: {acronyms_json}\n\nterms_json: {terms_json}```"

    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': user_message},
    ]

    response = openai.ChatCompletion.create(
        model=config["model"],
        messages=messages,
        temperature=config["temperature"],
        max_tokens=2000,
    )

    return response.choices[0].message['content'] if response.choices else None



def rag(query, retriever):
    '''Runs a RAG completion on the modified query'''

    system_message_prompt_template = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=['context'],
        template="Use the following pieces of context to answer the users question. INCLUDES ALL OF THE DETAILS IN YOUR RESPONSE, INDLUDING REQUIREMENTS AND REGULATIONS. National Workshops are required for boat crew, aviation, and telecommunications when then are offered and you should mention this in questions about those programs. Include Auxiliary Core Training (AUXCT) in your response for any question regarding certifications or officer positions.  \nIf you don't know the answer, just say I don't know, don't try to make up an answer. \n----------------\n{context}"
        )
    )

    llm_chain = LLMChain(
        prompt=ChatPromptTemplate(input_variables=['context', 'question'], messages=[system_message_prompt_template, HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['question'], template='{question}'))]),
        llm=llm,
        )

    rag_instance = RetrievalQA(
        combine_documents_chain=StuffDocumentsChain(
            llm_chain=llm_chain, document_variable_name='context'),
        return_source_documents=True,
        retriever=retriever
    )

    response = rag_instance({"query": query})
    return response



def rag_dummy(query, retriever):
    '''A bug-fixing utility.
    
    Returns a dummy canned response instead of calling the LLM
    '''

    with open("config/dummy_response.pkl", "rb") as file:
        dummy_response = pickle.load(file)
    return dummy_response
        


def create_short_source_list(response):
    '''Extracts a list of sources with no description 
    
    The dictionary has three elements (query, response, and source_documents). 
    Inside the third is a list with a custom object Document 
    associated with the key 'source_documents'
    '''

    markdown_list = []
    
    for i, doc in enumerate(response['source_documents'], start=1):
        page_content = doc.page_content  
        source = doc.metadata['source']  
        short_source = source.split('/')[-1].split('.')[0]  
        page = doc.metadata['page']  
        markdown_list.append(f"*{short_source}*, page {page}\n")
    
    short_source_list = '\n'.join(markdown_list)
    return short_source_list



def create_long_source_list(response):
    '''Extracts a list of sources along with full source
    
    Response is a dictionary with three keys:
    ['query', 'result', 'source_documents']
    source_documents is a list with a LangChain custom Document object
    '''
    
    markdown_list = []
    
    for i, doc in enumerate(response['source_documents'], start=1):
        page_content = doc.page_content  
        source = doc.metadata['source']  
        short_source = source.split('/')[-1].split('.')[0]  
        page = doc.metadata['page']  
        markdown_list.append(f"**Reference {i}:**    *{short_source}*, page {page}   {page_content}\n")
    
    long_source_list = '\n'.join(markdown_list)
    return long_source_list



def count_tokens(response):
    '''Counts the tokens from the response'''

    encoding = tiktoken.encoding_for_model(config["model"])
     
    # Count tokens for the query
    query_tokens = encoding.encode(response['query'])
    query_length = len(query_tokens)
    
    # Count tokens for the source documents
    source_documents = response['source_documents']
    if isinstance(source_documents, list):
        source_tokens = encoding.encode(' '.join(map(str, source_documents)))
    else:
        source_tokens = encoding.encode(str(source_documents))
    source_length = len(source_tokens)
    
    # Count tokens for the result
    result_tokens = encoding.encode(response['result'])
    result_length = len(result_tokens)
    
    # Count total tokens
    total_tokens = query_length + source_length + result_length  
    return query_length, source_length, result_length, total_tokens



# Example usage in another script
if __name__ == "__main__":
    # Replace 'your_query' with the actual query you want to pass to rag
    query = 'your_query'
    response = rag(query, retriever) #thisn is slightly different from the notebook
    
    # Call other functions to process the response
    short_source_list = create_short_source_list(response)
    long_source_list = create_long_source_list(response)
    query_length, source_length, result_length, total_tokens = count_tokens(response)





