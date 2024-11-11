import streamlit as st
import requests
from typing import Optional
import json

# PR Agents configuration
PR_AGENTS = {
    "Media Relations": {
        "model": "gpt-4",
        "instructions": """
        **Media Relations Agent Instructions:**
        1. Share your press release draft or media query
        2. The agent will review and enhance media communications
        3. Focus on newsworthy angles and media-friendly formatting
        """
    },
    "Crisis Comms": {
        "model": "gpt-4",
        "instructions": """
        **Crisis Communications Agent Instructions:**
        1. Describe the situation or share crisis statement
        2. The agent will help craft appropriate responses
        3. Focus on reputation management and stakeholder communication
        """
    },
    "Content Strategy": {
        "model": "gpt-4",
        "instructions": """
        **Content Strategy Agent Instructions:**
        1. Share your content goals or materials
        2. The agent will provide strategic recommendations
        3. Focus on brand voice, messaging, and content optimization
        """
    },
    "Social Media": {
        "model": "gpt-4",
        "instructions": """
        **Social Media PR Agent Instructions:**
        1. Share your social media content or campaign ideas
        2. The agent will optimize for platform-specific engagement
        3. Focus on trending topics and audience engagement
        """
    },
    "Analytics": {
        "model": "gpt-4",
        "instructions": """
        **PR Analytics Agent Instructions:**
        1. Share your PR campaign data or metrics
        2. The agent will analyze performance and impact
        3. Focus on KPIs, sentiment analysis, and ROI measurement
        """
    }
}

def main():
    st.title("PR Agent Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Create tabs for each agent
    agent_tabs = st.tabs(list(PR_AGENTS.keys()))
    
    for tab, (agent_name, agent_info) in zip(agent_tabs, PR_AGENTS.items()):
        with tab:
            # Instructions section
            with st.expander("Instructions", expanded=False):
                st.markdown(agent_info['instructions'])
            
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat input
            if user_input := st.chat_input(f"Message {agent_name}..."):
                with st.spinner('Processing...'):
                    try:
                        data = {
                            "query": user_input,
                            "agent_type": agent_name,
                            "model": agent_info['model']
                        }
                        
                        response = requests.post(
                            'http://localhost:8000/api/pr-agent',
                            json=data,
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result['status'] == 'success':
                                st.session_state.messages.extend([
                                    {"role": "user", "content": user_input},
                                    {"role": "assistant", "content": result['response']}
                                ])
                                st.rerun()
                            else:
                                st.error(f"Server error: {response.text}")
                        else:
                            st.error(f"Server error: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to backend server. Please make sure it's running on port 8000.")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()