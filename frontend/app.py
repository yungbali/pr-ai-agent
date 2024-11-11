import streamlit as st
import requests
import json
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="PR AI Agent Suite",
    page_icon="✨",
    layout="wide"
)

# Initialize session state for each agent
if 'sentiment_messages' not in st.session_state:
    st.session_state.sentiment_messages = []
if 'content_messages' not in st.session_state:
    st.session_state.content_messages = []
if 'crisis_messages' not in st.session_state:
    st.session_state.crisis_messages = []
if 'visual_messages' not in st.session_state:
    st.session_state.visual_messages = []
if 'embedding_messages' not in st.session_state:
    st.session_state.embedding_messages = []

def fetch_pr_tasks():
    """Fetch available PR tasks from the backend"""
    try:
        response = requests.get('http://localhost:8000/api/pr-tasks')
        return response.json()['tasks']
    except Exception as e:
        st.error(f"Error fetching PR tasks: {str(e)}")
        return {}

def send_message(message: str, task_type: str, uploaded_file: Optional[bytes] = None):
    """Send message to backend API"""
    try:
        files = {}
        data = {
            'query': message,
            'task_type': task_type
        }
        
        if uploaded_file:
            files['file'] = uploaded_file

        response = requests.post(
            'http://localhost:8000/api/pr-agent',
            data=data,
            files=files
        )
        
        return response.json()
    except Exception as e:
        st.error(f"Error communicating with backend: {str(e)}")
        return None

def clear_chat(agent_type: str):
    """Clear chat history for specific agent"""
    if f'{agent_type}_messages' in st.session_state:
        st.session_state[f'{agent_type}_messages'] = []

def display_how_to(agent_type: str):
    """Display how-to guide for specific agent"""
    how_to_guides = {
        'sentiment': """
        ### How to use Sentiment Analysis Agent
        1. **Input**: Paste your text content (articles, social media posts, comments)
        2. **Optional**: Upload related files for context
        3. **Output**: Receive detailed sentiment analysis including:
            - Overall sentiment (positive/negative/neutral)
            - Key themes and topics
            - Emotional intensity
            - Potential PR implications
        """,
        
        'content': """
        ### How to use Content Creation Agent
        1. **Input**: Provide context and requirements for your content
        2. **Optional**: Upload brand guidelines or reference materials
        3. **Output**: Receive professionally crafted content including:
            - Press releases
            - Social media posts
            - Blog articles
            - Media statements
        """,
        
        'crisis': """
        ### How to use Crisis Management Agent
        1. **Input**: Describe the crisis situation
        2. **Optional**: Upload relevant documents or media coverage
        3. **Output**: Receive:
            - Strategic response statements
            - Stakeholder communication plans
            - Action item recommendations
            - Risk mitigation strategies
        """,
        
        'visual': """
        ### How to use Visual Content Agent
        1. **Input**: Describe your desired image or visual content
        2. **Optional**: Upload reference images or brand guidelines
        3. **Output**: Receive:
            - AI-generated images for PR campaigns
            - Visual concept descriptions
            - Brand-aligned visual recommendations
        """,
        
        'embedding': """
        ### How to use Content Embedding Agent
        1. **Input**: Provide text for analysis
        2. **Optional**: Upload documents for comparison
        3. **Output**: Receive:
            - Vector embeddings for content analysis
            - Content similarity metrics
            - Semantic search capabilities
        """
    }
    st.markdown(how_to_guides[agent_type])

# Main UI
st.title("PR AI Agent Suite")

# Create tabs for each agent
tabs = st.tabs([
    "Sentiment Analysis", 
    "Content Creation", 
    "Crisis Management",
    "Visual Content",
    "Content Embedding"
])

# Fetch PR tasks once
pr_tasks = fetch_pr_tasks()

# Sentiment Analysis Tab
with tabs[0]:
    col1, col2 = st.columns([2,1])
    with col1:
        st.header("Sentiment Analysis Agent")
        
        # Clear chat button
        if st.button("Clear Chat", key="clear_sentiment"):
            clear_chat('sentiment')
        
        # File uploader
        uploaded_file = st.file_uploader("Upload a file (optional)", 
            type=['txt', 'pdf', 'docx'], key="file_sentiment")
        
        # Message input
        message = st.text_area("Enter text for sentiment analysis", height=100, key="input_sentiment")
        
        if st.button("Analyze", type="primary", key="send_sentiment"):
            if message:
                st.session_state.sentiment_messages.append({"role": "user", "content": message})
                response = send_message(message, "sentiment_analysis", 
                    uploaded_file.read() if uploaded_file else None)
                if response and response.get('status') == 'success':
                    st.session_state.sentiment_messages.append(
                        {"role": "assistant", "content": response['response']['analysis']})
        
        # Display chat history
        for msg in st.session_state.sentiment_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    with col2:
        display_how_to('sentiment')

# Content Creation Tab
with tabs[1]:
    col1, col2 = st.columns([2,1])
    with col1:
        st.header("Content Creation Agent")
        
        if st.button("Clear Chat", key="clear_content"):
            clear_chat('content')
            
        uploaded_file = st.file_uploader("Upload a file (optional)", 
            type=['txt', 'pdf', 'docx'], key="file_content")
            
        message = st.text_area("Enter content requirements", height=100, key="input_content")
        
        if st.button("Generate", type="primary", key="send_content"):
            if message:
                st.session_state.content_messages.append({"role": "user", "content": message})
                response = send_message(message, "content_creation", 
                    uploaded_file.read() if uploaded_file else None)
                if response and response.get('status') == 'success':
                    st.session_state.content_messages.append(
                        {"role": "assistant", "content": response['response']['content']})
        
        for msg in st.session_state.content_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    with col2:
        display_how_to('content')

# Crisis Management Tab
with tabs[2]:
    col1, col2 = st.columns([2,1])
    with col1:
        st.header("Crisis Management Agent")
        
        if st.button("Clear Chat", key="clear_crisis"):
            clear_chat('crisis')
            
        uploaded_file = st.file_uploader("Upload a file (optional)", 
            type=['txt', 'pdf', 'docx'], key="file_crisis")
            
        message = st.text_area("Describe the crisis situation", height=100, key="input_crisis")
        
        if st.button("Get Response", type="primary", key="send_crisis"):
            if message:
                st.session_state.crisis_messages.append({"role": "user", "content": message})
                response = send_message(message, "crisis_management", 
                    uploaded_file.read() if uploaded_file else None)
                if response and response.get('status') == 'success':
                    st.session_state.crisis_messages.append(
                        {"role": "assistant", "content": response['response']['response']})
        
        for msg in st.session_state.crisis_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    with col2:
        display_how_to('crisis')

# Visual Content Tab
with tabs[3]:
    col1, col2 = st.columns([2,1])
    with col1:
        st.header("Visual Content Agent")
        
        if st.button("Clear Chat", key="clear_visual"):
            clear_chat('visual')
            
        uploaded_file = st.file_uploader("Upload a reference image (optional)", 
            type=['png', 'jpg', 'jpeg'], key="file_visual")
            
        message = st.text_area("Describe the desired image", height=100, key="input_visual")
        
        if st.button("Generate Image", type="primary", key="send_visual"):
            if message:
                st.session_state.visual_messages.append({"role": "user", "content": message})
                response = send_message(message, "visual_content", 
                    uploaded_file.read() if uploaded_file else None)
                if response and response.get('status') == 'success':
                    st.session_state.visual_messages.append(
                        {"role": "assistant", "content": response['response']['image_url']})
                    st.image(response['response']['image_url'])
        
        for msg in st.session_state.visual_messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    st.image(msg["content"])
                else:
                    st.markdown(msg["content"])
    
    with col2:
        display_how_to('visual')

# Content Embedding Tab
with tabs[4]:
    col1, col2 = st.columns([2,1])
    with col1:
        st.header("Content Embedding Agent")
        
        if st.button("Clear Chat", key="clear_embedding"):
            clear_chat('embedding')
            
        uploaded_file = st.file_uploader("Upload a file (optional)", 
            type=['txt', 'pdf', 'docx'], key="file_embedding")
            
        message = st.text_area("Enter text for embedding", height=100, key="input_embedding")
        
        if st.button("Generate Embedding", type="primary", key="send_embedding"):
            if message:
                st.session_state.embedding_messages.append({"role": "user", "content": message})
                response = send_message(message, "content_embedding", 
                    uploaded_file.read() if uploaded_file else None)
                if response and response.get('status') == 'success':
                    st.session_state.embedding_messages.append(
                        {"role": "assistant", "content": str(response['response']['embedding'])})
        
        for msg in st.session_state.embedding_messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    st.json(msg["content"])
                else:
                    st.markdown(msg["content"])
    
    with col2:
        display_how_to('embedding')

# Footer
st.markdown("---")
st.markdown("PR AI Agent Suite - Powered by Afromuse Digital")