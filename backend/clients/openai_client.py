from openai import OpenAI
import os
from typing import Dict, List
from ..config import OPENAI_API_CONFIG

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def generate_response(self, messages: List[Dict[str, str]], **kwargs):
        try:
            completion = self.client.chat.completions.create(
                model=kwargs.get('name', 'gpt-4'),
                messages=messages,
                temperature=kwargs.get('temperature', OPENAI_API_CONFIG["temperature"]),
                max_tokens=kwargs.get('max_tokens', OPENAI_API_CONFIG["max_tokens"]),
                stream=True
            )
            
            response_text = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    response_text += chunk.choices[0].delta.content

            # Return only the formatted content
            return response_text
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _format_response(self, text: str) -> str:
        """Format the response text with proper markdown"""
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        
        formatted_text = ""
        
        for para in paragraphs:
            # Check if it's a list item
            if para.strip().startswith(('1.', '2.', '3.', '-', '*')):
                formatted_text += para + "\n\n"
            # Check if it's a heading
            elif para.strip().startswith('#'):
                formatted_text += para + "\n\n"
            # Regular paragraph
            else:
                formatted_text += para + "\n\n"
        
        return formatted_text.strip()

    async def generate_image(self, prompt: str, **kwargs):
        try:
            response = self.client.images.generate(
                model=kwargs.get('name', 'dall-e-3'),
                prompt=prompt,
                size=kwargs.get('size', "1024x1024"),
                quality=kwargs.get('quality', "standard"),
                n=1
            )
            return {
                "image_url": response.data[0].url,
                "model_info": {
                    "name": kwargs.get('name', 'dall-e-3'),
                    "provider": "openai"
                }
            }
        except Exception as e:
            raise Exception(f"DALL-E API error: {str(e)}")