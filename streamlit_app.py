import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import json

# Initialize API clients with simple error handling
def init_clients():
    missing_keys = []
    api_keys = {}
    
    # Check for required API keys
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "NVIDIA_API_KEY"]:
        try:
            api_keys[key] = st.secrets[key]
        except KeyError:
            missing_keys.append(key)
    
    # If any keys are missing, show error and stop
    if missing_keys:
        st.error(f"Missing API keys: {', '.join(missing_keys)}")
        st.info("Please add these keys in your Streamlit Cloud settings")
        st.stop()
    
    return {
        "openai": OpenAI(api_key=api_keys["OPENAI_API_KEY"]),
        "anthropic": Anthropic(api_key=api_keys["ANTHROPIC_API_KEY"]),
        "nvidia_key": api_keys["NVIDIA_API_KEY"]
    }

# Initialize clients
clients = init_clients()

# Your app code starts here
st.title("AI Chat Application")