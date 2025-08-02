import os
import streamlit as st

from retriever import init_chatiyp_model

st.set_page_config(page_title="ChatIYP", layout="wide")

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = ""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "ai", "content": "Hello, what can I help with?"}]

# Title and description
st.title("🌐🤖 ChatIYP: Enabling natural language access to the Internet Yellow Pages")
st.info("🔎 This is a demo of a GPT-3.5-Turbo-powered chatbot that leverages Retrieval-Augmented Generation (RAG) to answer questions on the Internet Yellow Pages (IYP) knowledge graph.")

st.markdown("""
### Some examples queries you can test or get inspired
- What is the name of AS2497
- Which ASN originates the prefix 8.8.8.0/24
- What is the country and name of AS2497
- Countries of IXPs where AS2497 is present
- Select domain names that resolve to an IP originated by AS5470
- Select AS dependencies for AS5470
""")

st.warning("⚠️ The demo is in experimental phase. Usually it works well for questions similar to the above examples. For custom questions (especially too complex or too abstract) it may have problems in generating a good answer.")

st.warning("⚠️ Currently (experimental phase), the answers of the AI agent are limited to 10 items (e.g., if you ask which prefixes does an ASN originates, the answer will contain at most 10 prefixes)")

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

    with st.chat_message("ai"):
        message_placeholder = st.empty()
        expander_placeholder = st.empty()
        try:
            # Generate assistant response
            with st.spinner("Generating response..."):
                answer = str(st.session_state.query_engine.query(prompt))
                cypher = st.session_state.sub_retriever.generated_cypher_query

            # Store and display assistant message
            st.session_state.messages.append({"role": "ai", "content": answer, "cypher": cypher})
            message_placeholder.write(answer)
            with expander_placeholder.expander("Show Cypher query"):
                st.code(cypher, language="cypher")
        except:
            error_message = f"⚠️ An error occurred while generating a response."
            st.session_state.messages.append({"role": "ai", "content": error_message})
            message_placeholder.write(error_message)
        