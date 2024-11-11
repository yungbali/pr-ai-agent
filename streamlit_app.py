import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import json

# For local testing - show what keys are available
if st.secrets["settings"].get("debug"):
    st.write("Available secret keys:", st.secrets.keys())

# Initialize API clients
try:
    openai_client = OpenAI(
        api_key=st.secrets["api_keys"]["OPENAI_API_KEY"]
    )
    anthropic_client = Anthropic(
        api_key=st.secrets["api_keys"]["ANTHROPIC_API_KEY"]
    )
    nvidia_api_key = st.secrets["api_keys"]["NVIDIA_API_KEY"]
except KeyError as e:
    st.error(f"Missing API key in secrets: {e}")
    st.info("Please check your .streamlit/secrets.toml file or Streamlit Cloud settings")
    st.stop()

# Now you can use the clients
st.success("API clients initialized successfully!")