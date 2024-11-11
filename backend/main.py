from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

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

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Model configurations
MODELS = {
    "gpt-4-turbo": {
        "name": "gpt-4-1106-preview",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "gpt-4": {
        "name": "gpt-4",
        "max_tokens": 2048,
        "temperature": 0.7
    },
    "gpt-3.5-turbo": {
        "name": "gpt-3.5-turbo",
        "max_tokens": 1024,
        "temperature": 0.7
    },
    "dall-e-3": {
        "name": "dall-e-3",
        "quality": "standard",
        "size": "1024x1024"
    },
    "embeddings": {
        "name": "text-embedding-ada-002"
    }
}

# Enhanced PR tasks with specific model assignments
PR_TASKS = {
    "sentiment_analysis": {
        "name": "Sentiment Analysis",
        "description": "Analyze sentiment and themes in content",
        "prompt": "Analyze the following content for sentiment and key themes:",
        "model": "gpt-4"  # More accurate for analysis
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
        response = client.images.generate(
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
        response = client.embeddings.create(
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
        response = client.chat.completions.create(
            model=model_config["model_name"],
            messages=[
                {"role": "system", "content": PR_TASKS["sentiment_analysis"]["prompt"]},
                {"role": "user", "content": text}
            ],
            temperature=model_config["parameters"]["temperature"],
            max_tokens=model_config["parameters"]["max_tokens"]
        )
        return {
            "analysis": response.choices[0].message.content,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def generate_content(context: str, content_type: str, model_config: Dict) -> Dict:
    """Enhanced content generation with dynamic model selection"""
    try:
        response = client.chat.completions.create(
            model=model_config["model_name"],
            messages=[
                {"role": "system", "content": f"You are a PR content specialist. Create {content_type} based on the following context:"},
                {"role": "user", "content": context}
            ],
            temperature=model_config["parameters"]["temperature"],
            max_tokens=model_config["parameters"]["max_tokens"]
        )
        return {
            "content": response.choices[0].message.content,
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def handle_crisis(situation: str, model_config: Dict) -> Dict:
    """Enhanced crisis management with dynamic model selection"""
    try:
        response = client.chat.completions.create(
            model=model_config["model_name"],
            messages=[
                {"role": "system", "content": "You are a crisis management expert. Draft an appropriate response statement for the following situation:"},
                {"role": "user", "content": situation}
            ],
            temperature=model_config["parameters"]["temperature"],
            max_tokens=model_config["parameters"]["max_tokens"]
        )
        return {
            "response": response.choices[0].message.content,
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
    task_type: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    try:
        # Get model configuration for the task
        model_config = await select_model(task_type, query)
        if "error" in model_config:
            return {"response": model_config["error"], "status": "error"}
            
        # Handle file content if provided
        file_content = ""
        if file:
            file_content = (await file.read()).decode('utf-8')
            
        # Combine query and file content
        full_content = f"{query}\n{file_content}" if file_content else query
        
        # Add model information to the response
        result = {
            "model_used": model_config["model_name"],
            "parameters": model_config["parameters"]
        }
        
        # Route to appropriate task handler with model config
        if task_type == "sentiment_analysis":
            analysis = await analyze_sentiment(full_content, model_config)
            result.update(analysis)
        elif task_type == "content_creation":
            content = await generate_content(full_content, "press release", model_config)
            result.update(content)
        elif task_type == "crisis_management":
            response = await handle_crisis(full_content, model_config)
            result.update(response)
        elif task_type == "visual_content":
            image = await generate_image(full_content)
            result.update(image)
        elif task_type == "content_embedding":
            embedding = await generate_embeddings(full_content)
            result.update(embedding)
        else:
            return {"response": "Invalid task type", "status": "error"}
            
        return {"response": result, "status": "success"}
        
    except Exception as e:
        return {"response": f"Error: {str(e)}", "status": "error"}

@app.get("/api/pr-tasks")
async def get_pr_tasks():
    """Return available PR tasks"""
    return {"tasks": PR_TASKS}

@app.get("/api/models")
async def get_models():
    """Return available models and their configurations"""
    return {"models": MODELS}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)