from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.agent_config import PR_AGENTS
from .clients.nvidia_client import NvidiaClient
from .clients.openai_client import OpenAIClient
from .clients.anthropic_client import AnthropicClient

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize all clients
openai_client = OpenAIClient()
nvidia_client = NvidiaClient()
anthropic_client = AnthropicClient()

class ModelFailoverHandler:
    def __init__(self):
        self.clients = {
            "openai": openai_client,
            "nvidia": nvidia_client,
            "anthropic": anthropic_client
        }
        self.fallback_order = ["openai", "nvidia", "anthropic"]

    async def generate_with_fallback(self, messages: list, model_config: Dict):
        errors = []
        primary_provider = model_config.get("provider", "openai")
        
        # Try primary provider first
        try:
            return await self.clients[primary_provider].generate_response(messages, **model_config)
        except Exception as e:
            errors.append(f"{primary_provider} error: {str(e)}")

        # Try fallbacks in order
        for provider in self.fallback_order:
            if provider != primary_provider:
                try:
                    fallback_config = MODELS.get(f"{provider}-fallback", model_config)
                    return await self.clients[provider].generate_response(messages, **fallback_config)
                except Exception as e:
                    errors.append(f"{provider} error: {str(e)}")

        # If all providers fail, raise exception with all errors
        raise Exception(f"All providers failed: {'; '.join(errors)}")

failover_handler = ModelFailoverHandler()

# Model configurations
MODELS = {
    "gpt-4-turbo": {
        "name": "gpt-4-1106-preview",
        "max_tokens": 4096,
        "temperature": 0.7,
        "provider": "openai"
    },
    "gpt-4": {
        "name": "gpt-4",
        "max_tokens": 2048,
        "temperature": 0.7,
        "provider": "openai"
    },
    "gpt-3.5-turbo": {
        "name": "gpt-3.5-turbo",
        "max_tokens": 1024,
        "temperature": 0.7,
        "provider": "openai"
    },
    "dall-e-3": {
        "name": "dall-e-3",
        "quality": "standard",
        "size": "1024x1024"
    },
    "embeddings": {
        "name": "text-embedding-ada-002"
    },
    "nvidia-llama": {
        "name": "nvidia/llama-3.1-nemotron-70b-instruct",
        "max_tokens": 1024,
        "temperature": 0.7,
        "provider": "nvidia"
    }
}

# Enhanced PR tasks with specific model assignments
PR_TASKS = {
    "sentiment_analysis": {
        "name": "Sentiment Analysis",
        "description": "Analyze sentiment and themes in content",
        "prompt": "Analyze the following content for sentiment and key themes:",
        "model": "nvidia-llama"  # Using NVIDIA's model
    },
    "content_creation": {
        "name": "Content Creation",
        "description": "Generate PR content and materials",
        "prompt": "Create PR content for the following context:",
        "model": "gpt-4-turbo"  # Better for creative tasks
    },
    "crisis_management": {
        "name": "Crisis Management",
        "description": "Draft crisis response statements",
        "prompt": "Draft a crisis response statement for the following situation:",
        "model": "gpt-4"  # More reliable for sensitive content
    },
    "visual_content": {
        "name": "Visual Content",
        "description": "Generate PR-related images",
        "prompt": "Generate a PR campaign image based on:",
        "model": "dall-e-3"
    },
    "content_embedding": {
        "name": "Content Embedding",
        "description": "Generate embeddings for content analysis",
        "model": "embeddings"
    }
}

async def generate_image(prompt: str) -> Dict:
    """Use DALL-E 3 for image generation"""
    try:
        response = openai_client.client.images.generate(
            model=MODELS["dall-e-3"]["name"],
            prompt=prompt,
            size=MODELS["dall-e-3"]["size"],
            quality=MODELS["dall-e-3"]["quality"],
            n=1
        )
        return {
            "image_url": response.data[0].url,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def generate_embeddings(text: str) -> Dict:
    """Generate embeddings for text analysis"""
    try:
        response = openai_client.client.embeddings.create(
            model=MODELS["embeddings"]["name"],
            input=text
        )
        return {
            "embedding": response.data[0].embedding,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def analyze_sentiment(text: str, model_config: Dict) -> Dict:
    """Enhanced sentiment analysis with dynamic model selection"""
    try:
        messages = [
            {"role": "system", "content": PR_TASKS["sentiment_analysis"]["prompt"]},
            {"role": "user", "content": text}
        ]
        response = await failover_handler.generate_with_fallback(messages, model_config)
        return {
            "analysis": response,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def generate_content(context: str, content_type: str, model_config: Dict) -> Dict:
    """Enhanced content generation with dynamic model selection"""
    try:
        messages = [
            {"role": "system", "content": f"You are a PR content specialist. Create {content_type} based on the following context:"},
            {"role": "user", "content": context}
        ]
        response = await failover_handler.generate_with_fallback(messages, model_config)
        return {
            "content": response,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def handle_crisis(situation: str, model_config: Dict) -> Dict:
    """Enhanced crisis management with dynamic model selection"""
    try:
        messages = [
            {"role": "system", "content": "You are a crisis management expert. Draft an appropriate response statement for the following situation:"},
            {"role": "user", "content": situation}
        ]
        response = await failover_handler.generate_with_fallback(messages, model_config)
        return {
            "response": response,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def select_model(task_type: str, content: str) -> Dict:
    """Select appropriate model and parameters based on task type and content"""
    task = PR_TASKS.get(task_type)
    if not task:
        return {"error": "Invalid task type"}
        
    model_key = task.get("model")
    model_config = MODELS.get(model_key, MODELS["gpt-3.5-turbo"])
    
    return {
        "model_name": model_config["name"],
        "parameters": {
            "max_tokens": model_config.get("max_tokens", 1024),
            "temperature": model_config.get("temperature", 0.7),
            "quality": model_config.get("quality", "standard"),
            "size": model_config.get("size", "1024x1024")
        }
    }

@app.post("/api/pr-agent")
async def pr_agent(
    query: str = Form(...),
    agent_type: str = Form(...),
    model: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    try:
        agent = PR_AGENTS.get(agent_type)
        if not agent:
            raise HTTPException(status_code=400, detail="Invalid agent type")

        model_config = MODELS.get(model)
        if not model_config:
            raise HTTPException(status_code=400, detail="Invalid model configuration")

        # For visual creator, first generate prompt using NVIDIA model
        if agent_type == "visual_creator":
            # First, get detailed prompt from NVIDIA
            nvidia_messages = [
                {"role": "system", "content": "You are a visual content expert. Create a detailed visual description for DALL-E image generation based on the following request:"},
                {"role": "user", "content": query}
            ]
            
            nvidia_response = await nvidia_client.generate_response(
                nvidia_messages,
                **MODELS["nvidia-llama"]
            )
            
            # Then use the generated description for DALL-E
            dalle_prompt = nvidia_response["content"]
            image_response = await openai_client.generate_image(
                dalle_prompt,
                **MODELS["dall-e-3"]
            )
            
            return {
                "response": {
                    "prompt": dalle_prompt,
                    "image_url": image_response["image_url"]
                },
                "status": "success"
            }

        # For other agent types, proceed with normal text generation
        system_prompt = f"You are a {agent['title']}. {agent['description']}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]

        if file:
            file_content = (await file.read()).decode('utf-8')
            messages[1]["content"] = f"{query}\n\nFile content:\n{file_content}"

        response = await failover_handler.generate_with_fallback(messages, model_config)

        return {
            "response": response,
            "status": "success"
        }

    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "status": "error"
        }

@app.get("/api/pr-tasks")
async def get_pr_tasks():
    return {
        "tasks": {
            "review": {
                "name": "Code Review",
                "description": "Review code changes and provide feedback",
                "prompt": "Please review these code changes:"
            },
            "explain": {
                "name": "Code Explanation",
                "description": "Explain what the code does",
                "prompt": "Please explain what this code does:"
            },
            "suggest": {
                "name": "Suggestions",
                "description": "Suggest improvements to the code",
                "prompt": "Please suggest improvements for this code:"
            }
        }
    }

@app.get("/api/models")
async def get_models():
    """Return available models and their configurations"""
    return {"models": MODELS}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)