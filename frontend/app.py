import streamlit as st
import requests
from typing import Optional
import json

# PR Agents configuration
PR_AGENTS = {
    "content_strategist": {
        "title": "Content Strategist",
        "description": "Content creation and brand voice management",
        "placeholder": "What content would you like me to help with?",
        "model": "gpt-4-turbo"
    },
    "crisis_manager": {
        "title": "Crisis Manager",
        "description": "Crisis response and risk management",
        "placeholder": "Describe the situation that needs addressing...",
        "model": "gpt-4"
    },
    "media_relations": {
        "title": "Media Relations",
        "description": "Press releases and media communications",
        "placeholder": "What would you like to communicate to the media?",
        "model": "gpt-4-turbo"
    },
    "analytics_expert": {
        "title": "Analytics Expert",
        "description": "Content and sentiment analysis",
        "placeholder": "What would you like me to analyze?",
        "model": "claude-3"
    },
    "visual_creator": {
        "title": "Visual Creator",
        "description": "Visual content generation and guidance",
        "placeholder": "Describe the visual content you need...",
        "model": "dall-e-3"
    }
}

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Page config
st.title("PR AI Agent")

# Agent selection
selected_agent = st.selectbox(
    "Select PR Agent",
    options=list(PR_AGENTS.keys()),
    format_func=lambda x: PR_AGENTS[x]["title"]
)

# Display agent info
if selected_agent:
    st.info(PR_AGENTS[selected_agent]["description"])

# Input area
user_input = st.text_area(
    "Message",
    placeholder=PR_AGENTS[selected_agent]["placeholder"],
    height=150
)

# File uploader
uploaded_file = st.file_uploader(
    "Upload a file (optional)",
    type=['txt', 'md', 'pdf', 'doc', 'docx']
)

# Send button
if st.button("Send", type="primary"):
    if user_input or uploaded_file:
        with st.spinner('Processing...'):
            try:
                # Prepare the request data
                data = {
                    'query': user_input,
                    'agent_type': selected_agent,
                    'model': PR_AGENTS[selected_agent]['model']
                }
                
                files = {}
                if uploaded_file:
                    files = {'file': uploaded_file.getvalue()}

                # Make API call
                response = requests.post(
                    'http://localhost:8000/api/pr-agent',
                    data=data,
                    files=files
                )
                
                result = response.json()
                
                if result['status'] == 'success':
                    # Add messages to history with clean format
                    st.session_state.messages.extend([
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": result['response']}
                    ])
                    st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Display messages
if st.session_state.messages:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])