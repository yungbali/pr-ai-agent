from anthropic import Anthropic
import os
from typing import Dict, List
from ..config import ANTHROPIC_API_CONFIG

class AnthropicClient:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.default_model = ANTHROPIC_API_CONFIG["default_model"]

    async def generate_response(self, messages: List[Dict[str, str]], **kwargs):
        try:
            # Convert chat format to Anthropic format
            prompt = "\n\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            message = self.client.messages.create(
                model=kwargs.get('name', self.default_model),
                max_tokens=kwargs.get('max_tokens', ANTHROPIC_API_CONFIG["max_tokens"]),
                temperature=kwargs.get('temperature', ANTHROPIC_API_CONFIG["temperature"]),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return {
                "content": message.content[0].text,
                "model_info": {
                    "name": kwargs.get('name', self.default_model),
                    "provider": "anthropic"
                }
            }
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")

# Create instance
anthropic_client = AnthropicClient()