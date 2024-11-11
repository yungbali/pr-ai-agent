from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PRRequest(BaseModel):
    query: str
    agent_type: str
    model: str

@app.post("/api/pr-agent")
async def pr_agent(request: PRRequest):
    try:
        # Your existing logic here
        system_prompt = f"You are a {PR_AGENTS[request.agent_type]['title']}. {PR_AGENTS[request.agent_type]['description']}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.query}
        ]

        response = await failover_handler.generate_with_fallback(messages, {"name": request.model})

        return {
            "response": response,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))