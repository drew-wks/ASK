import streamlit as st 
import datetime, time, os, sys
from trubrics.integrations.streamlit import FeedbackCollector
import ASK_inference as ASK
from qdrant_client import QdrantClient
from ASK_inference import config
from streamlit_extras.stylable_container import stylable_container


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

@st.cache_resource
def qdrant_connect_cloud():
    os.write(1,b'QdrantClient start.\n')
    if 'client' in globals():
        return globals()['client']  # Return the existing client
    client = QdrantClient(
    "https://0c82e035-1105-40f2-a0bd-ecc44a016f15.us-east4-0.gcp.cloud.qdrant.io", 
    prefer_grpc=True,
    api_key=st.secrets.QDRANT_API_KEY,
    )
    os.write(1,b'QdrantClient complete.\n')
    return client

client = qdrant_connect_cloud()
qdrant = ASK.create_langchain_qdrant(client)
retriever = ASK.init_retriever_and_generator(qdrant)

user_feedback = " "
query = st.text_input("Type your question or task here", max_chars=200)
if query:
    os.write(1, f"query start: {datetime.datetime.now().strftime('%H:%M:%S')}\n".encode())
    with st.status("Checking documents...", expanded=False) as status:
        try:
            if query == "pledge":
                response = ASK.rag_dummy(query, retriever)  # ASK.rag_dummy for UNIT TESTING
            else:
                response = ASK.rag(query, retriever)

            short_source_list = ASK.create_short_source_list(response)
            long_source_list = ASK.create_long_source_list(response)

        except openai.error.RateLimitError:
            print("ASK has run out of Open AI credits. Tell Drew to go fund his account!")
            response = None  

        except Exception as e:
            print(f"An error occurred: {e} Please try ASK again later")
            response = None  

        os.write(1, f"complete:    {datetime.datetime.now().strftime('%H:%M:%S')}\n".encode())


        st.info(f"**Question:** *{query}*\n\n ##### Response:\n{response['result']}\n\n **Sources:**  \n{short_source_list}\n **Note:** \n ASK can make mistakes. Verify the sources and check for local policy.")

    status.update(label=":blue[**Response**]", expanded=True)

    with st.status("Compiling references...", expanded=False) as status:
        time.sleep(1)
        st.write(long_source_list)
        status.update(label=":blue[CLICK HERE FOR FULL SOURCE DETAILS]", expanded=False)
