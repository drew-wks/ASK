
import streamlit as st
import ASK_inference as ASK
import time
from ASK_inference import config

api_key=st.secrets.QDRANT_API_KEY


# Check if 'client' is not in locals() or 'client' is not in globals()
#if not it runs qdrant_check_and_connect()
#and places the client object into st.session_state
if 'clientkey' not in st.session_state:
    st.session_state.clientkey = []
    client = ASK.qdrant_connect_cloud(api_key)
    st.session_state.clientkey = client
    print(st.session_state.clientkey)


qdrant = ASK.create_langchain_qdrant(st.session_state.clientkey)
retriever = ASK.init_retriever_and_generator(qdrant)


st.image("https://raw.githubusercontent.com/dvvilkins/ASK/main/images/ASK_logotype_color.png?raw=true", use_column_width="always")
st.write("#### Get answers to USCG Auxiliary questions from authoritative sources.")
st.write("ASK uses Artificial Intelligence (AI) to search over [250](https://github.com/dvvilkins/ASK/blob/0e975f41f8f072aac2837ac42a9fe11963dc3fb2/docs/library_doc_list.pdf) Coast Guard Auxiliary references to answer your questions.  Please note: ASK is offered on evaluation basis and has not been officially adopted by the USCG Auxiliary. For questions or feedback, contact [Drew Wilkins](mailto:uscgaux.drew@wks.us).", unsafe_allow_html=True)

st.markdown('<a href="/2_Library" target="_self">linke</a>', unsafe_allow_html=True)

#response = {}
query = st.chat_input("Type your question or task here", max_chars=200)
if query:
    response = ASK.rag_dummy(query,retriever) # ADDING A DUMMY FUNCTION FOR UNIT TESTING
    short_source_list = ASK.create_short_source_list(response)
    long_source_list = ASK.create_long_source_list(response)
    st.info(f"""##### Response:\n{response['result']}\n\n **Sources:**  \n {short_source_list}\n**Note:**  \nASK may contain inaccuracies. Please review the official documents. Also, ASK only searches natonal documents. Check with your district, division and flotilla leadership for official policy in your AOR.
    """)

###############
    with st.status("Compiling references...", expanded=False) as status:
        time.sleep(1)
        st.write(long_source_list)
        status.update(label=":blue[**Click for references**]", expanded=False)
