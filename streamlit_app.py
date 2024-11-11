import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import json

# Initialize API clients with more graceful error handling
try:
    openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("OpenAI API key not found in secrets. Please add it in Streamlit Cloud.")
    st.stop()

try:
    anthropic_client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
except KeyError:
    st.error("Anthropic API key not found in secrets. Please add it in Streamlit Cloud.")
    st.stop()

try:
    nvidia_api_key = st.secrets["NVIDIA_API_KEY"]
except KeyError:
    st.error("NVIDIA API key not found in secrets. Please add it in Streamlit Cloud.")
    st.stop()

# PR Agents Configuration
PR_AGENTS = {
    "Media Relations": {
        "title": "Media Relations Expert",
        "description": "Press releases and media communications specialist",
        "model": "gpt-4-turbo-preview",
        "instructions": """
        **Media Relations Agent Instructions:**
        1. Share your press release draft or media query
        2. Get expert review and enhancement of media communications
        3. Receive guidance on newsworthy angles and media-friendly formatting
        """
    },
    "Crisis Comms": {
        "title": "Crisis Communications Manager",
        "description": "Crisis response and reputation management",
        "model": "claude-3-opus-20240229",
        "instructions": """
        **Crisis Communications Agent Instructions:**
        1. Describe the situation or share crisis statement
        2. Get strategic guidance on crisis response
        3. Receive stakeholder communication recommendations
        """
    },
    "Content Strategy": {
        "title": "Content Strategist",
        "description": "Content planning and brand voice expert",
        "model": "gpt-4-turbo-preview",
        "instructions": """
        **Content Strategy Agent Instructions:**
        1. Share your content goals or materials
        2. Get strategic content recommendations
        3. Receive brand voice and messaging guidance
        """
    }
}

def generate_response(query: str, agent_type: str, model: str) -> str:
    """Generate response based on the model provider"""
    
    system_prompt = f"You are a {PR_AGENTS[agent_type]['title']}. {PR_AGENTS[agent_type]['description']}"
    
    try:
        if "claude" in model.lower():
            response = anthropic_client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": f"{system_prompt}\n\nUser Query: {query}"
                    }
                ]
            )
            return response.content[0].text
            
        else:  # OpenAI models
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
            
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def main():
    st.title("PR Agency Assistant")
    
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
                # Process the user input and generate a response
                response = generate_response(user_input, agent_name, agent_info['model'])
                
                # Add the user input and response to the chat history
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Display the response
                with st.chat_message("assistant"):
                    st.markdown(response)

if __name__ == "__main__":
    main() 