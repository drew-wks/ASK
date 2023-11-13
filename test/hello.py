import streamlit as st

st.set_page_config(page_title="Toy running Python 3.11")




query = st.text_input("Type your question or task here", max_chars=200, key=unique_key)

if query:
    st.write(f"You typed: {query}")

from streamlit_extras.stylable_container import stylable_container

if "messages" not in st.session_state:
    st.session_state["messages"] = []


def generate_response(prompt):
    return f"This is a response to: {prompt}", 0, 0, 0


for message in st.session_state["messages"][1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("Thinking..."):
        (
            full_response,
            total_tokens,
            prompt_tokens,
            completion_tokens,
        ) = generate_response(prompt)

    st.chat_message("assistant").write(full_response)
    st.session_state["messages"].append({"role": "assistant", "content": full_response})

with stylable_container(
    key="bottom_content",
    css_styles="""
        {
            position: fixed;
            bottom: 50px;
        }
        """,
):
    st.markdown("Some content")  # this appears above the chat_input() element.

st.markdown(
    """
    <style>
        .stChatFloatingInputContainer {
            bottom: 20px;
            background-color: rgba(0, 0, 0, 0)
        }
    </style>
    """,
    unsafe_allow_html=True,
)
