import streamlit as st
import os
from utils.failover import FailoverHandler
import asyncio

# Initialize API keys with more graceful error handling
try:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
    os.environ["NVIDIA_API_KEY"] = st.secrets["NVIDIA_API_KEY"]
except KeyError:
    st.error("Please set up your API keys in .streamlit/secrets.toml")
    st.stop()

# Initialize the FailoverHandler
failover_handler = FailoverHandler()

st.title("AI Chat with Multiple Models")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Model selection
model = st.selectbox(
    "Choose a model:",
    ["gpt-4", "claude-3-opus", "claude-3-sonnet", "nvidia/llama-3.1-nemotron-70b-instruct", "gpt-3.5-turbo"]
)

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            response = asyncio.run(failover_handler.generate_with_fallback(
                st.session_state.messages,
                {"name": model}
            ))
            message_placeholder.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            message_placeholder.error(f"Error: {str(e)}") 