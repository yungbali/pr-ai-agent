from typing import List, Dict, Any
import os
import openai
import anthropic
from openai import OpenAI  # Updated import for NVIDIA

class FailoverHandler:
    def __init__(self):
        # Initialize API clients
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.nvidia_client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )
        
        self.fallback_models = [
            {"name": "gpt-4", "provider": "openai"},
            {"name": "claude-3-opus", "provider": "anthropic"},
            {"name": "claude-3-sonnet", "provider": "anthropic"},
            {"name": "nvidia/llama-3.1-nemotron-70b-instruct", "provider": "nvidia"},
            {"name": "gpt-3.5-turbo", "provider": "openai"},
        ]
        
    async def generate_with_fallback(self, messages: List[Dict[str, str]], model_config: Dict[str, Any]) -> str:
        """
        Attempts to generate a response using different providers
        """
        requested_model = model_config.get("name")
        models_to_try = [m for m in self.fallback_models if m["name"] == requested_model] + \
                       [m for m in self.fallback_models if m["name"] != requested_model]
        
        last_error = None
        for model in models_to_try:
            try:
                if model["provider"] == "openai":
                    response = await self._generate_openai(messages, model["name"])
                elif model["provider"] == "anthropic":
                    response = await self._generate_anthropic(messages, model["name"])
                elif model["provider"] == "nvidia":
                    response = await self._generate_nvidia(messages, model["name"])
                return response
            except Exception as e:
                last_error = e
                continue
                
        raise Exception(f"All models failed. Last error: {str(last_error)}")

    async def _generate_openai(self, messages, model_name):
        response = await self.openai_client.chat.completions.create(
            model=model_name,
            messages=messages
        )
        return response.choices[0].message.content

    async def _generate_anthropic(self, messages, model_name):
        # Convert chat format to Anthropic format
        formatted_messages = self._format_for_anthropic(messages)
        response = await self.anthropic_client.messages.create(
            model=model_name,
            messages=formatted_messages
        )
        return response.content[0].text

    async def _generate_nvidia(self, messages, model_name):
        response = await self.nvidia_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.5,
            top_p=1,
            max_tokens=1024
        )
        return response.choices[0].message.content

    def _format_for_anthropic(self, messages):
        # Convert standard chat format to Anthropic's format
        formatted = []
        for msg in messages:
            role = "assistant" if msg["role"] == "assistant" else "user"
            formatted.append({"role": role, "content": msg["content"]})
        return formatted