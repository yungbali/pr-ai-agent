from openai import OpenAI
import os
from typing import Dict, List
from ..config import NVIDIA_API_CONFIG

class NvidiaClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=NVIDIA_API_CONFIG["base_url"],
            api_key=os.getenv("NVIDIA_API_KEY")
        )
        self.model_id = NVIDIA_API_CONFIG["model_id"]

    async def generate_response(self, messages: List[Dict[str, str]], **kwargs):
        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=kwargs.get('temperature', NVIDIA_API_CONFIG["temperature"]),
                top_p=kwargs.get('top_p', NVIDIA_API_CONFIG["top_p"]),
                max_tokens=kwargs.get('max_tokens', NVIDIA_API_CONFIG["max_tokens"]),
                stream=True
            )
            
            response_text = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response_text += chunk.choices[0].delta.content

            return {
                "content": response_text,
                "model_info": {
                    "name": self.model_id,
                    "provider": "nvidia"
                }
            }
            
        except Exception as e:
            raise Exception(f"NVIDIA API error: {str(e)}") 