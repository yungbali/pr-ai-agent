from typing import Dict

OPENAI_API_CONFIG = {
    "base_url": "https://integrate.api.nvidia.com/v1",
    "model_id": "nvidia/llama-3.1-nemotron-70b-instruct",
    "max_tokens": 1024,
    "temperature": 0.7,
    "top_p": 1
}

NVIDIA_API_CONFIG = {
    "base_url": "https://integrate.api.nvidia.com/v1",
    "model_id": "nvidia/llama-3.1-nemotron-70b-instruct",
    "max_tokens": 1024,
    "temperature": 0.7,
    "top_p": 1
}

ANTHROPIC_API_CONFIG = {
    "default_model": "claude-3-opus-20240229",
    "models": {
        "claude-3-opus": {
            "name": "claude-3-opus-20240229",
            "max_tokens": 4096,
            "temperature": 0.7
        },
        "claude-3-sonnet": {
            "name": "claude-3-sonnet-20240229",
            "max_tokens": 4096,
            "temperature": 0.7
        },
        "claude-2.1": {
            "name": "claude-2.1",
            "max_tokens": 4096,
            "temperature": 0.7
        }
    },
    "max_tokens": 4096,
    "temperature": 0.7
}

# Update the MODELS configuration
MODELS = {
    "nvidia-llama": {
        "name": "nvidia/llama-3.1-nemotron-70b-instruct",
        "max_tokens": 1024,
        "temperature": 0.7,
        "provider": "nvidia"
    },
    "gpt-4": {
        "name": "gpt-4",
        "max_tokens": 2048,
        "temperature": 0.7,
        "provider": "openai"
    },
    "claude-3": {
        "name": "claude-3-opus-20240229",
        "max_tokens": 4096,
        "temperature": 0.7,
        "provider": "anthropic"
    }
} 