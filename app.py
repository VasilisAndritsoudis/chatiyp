import os
import streamlit as st

from retriever import init_chatiyp_model

st.set_page_config(page_title="ChatIYP", layout="wide")

# Initialize session state key ONCE
if "api_key" not in st.session_state:
    st.session_state.api_key = None

if "OPENAI_API_KEY" not in os.environ:
    st.title("🔐 Enter your OpenAI API Key")
    api_key_input = st.text_input("API Key")
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input
        st.rerun()  # Reload app with key stored
    st.stop()  # Prevent rest of app from running
else:
    st.markdown(
        f"✅ **Using OpenAI API Key:** `{os.environ["OPENAI_API_KEY"][:6]}...{os.environ["OPENAI_API_KEY"][-4:]}`"
    )

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "ai", "content": "Hello, what can I help with?"}]

# Title and description
st.title("🤖 ChatIYP")
st.markdown(
    "🔎 A GPT-3.5-Turbo-powered chatbot that leverages Retrieval-Augmented Generation (RAG) to answer questions on the Internet Yellow Pages (IYP) knowledge graph."
)

# Connect to Neo4j only once
if "query_engine" not in st.session_state or "sub_retriever" not in st.session_state:
    with st.status("Connecting to Neo4j...", expanded=True) as status:
        query_engine, sub_retriever = init_chatiyp_model()
        st.session_state.query_engine = query_engine
        st.session_state.sub_retriever = sub_retriever
        status.update(label="Connected to Neo4j.", state="complete", expanded=False)
else:
    with st.status("Connecting to Neo4j...", expanded=True) as status:
        status.update(label="Connected to Neo4j.", state="complete", expanded=False)

# Display previous chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "ai" and "cypher" in msg:
            with st.expander("Show Cypher query"):
                st.code(msg["cypher"], language="cypher")

prompt = st.chat_input("Ask your question:")

if prompt:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate assistant response
    with st.status("Generating response...", expanded=True) as status:
        answer = str(st.session_state.query_engine.query(prompt))
        cypher = st.session_state.sub_retriever.generated_cypher_query
        status.update(label="Generated.", state="complete", expanded=False)

    # Store and display assistant message
    st.session_state.messages.append({"role": "ai", "content": answer, "cypher": cypher})
    with st.chat_message("ai"):
        st.write(answer)
        with st.expander("Show Cypher query"):
            st.code(cypher, language="cypher")
        