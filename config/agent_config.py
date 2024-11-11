# Shared configurations between frontend and backend
PR_AGENTS = {
    "content_strategist": {
        "title": "Content Strategist",
        "description": "Content creation and brand voice management",
        "placeholder": "What content would you like me to help with?",
        "model": "gpt-4-turbo"
    },
    "crisis_manager": {
        "title": "Crisis Manager",
        "description": "Crisis response and risk management",
        "placeholder": "Describe the situation that needs addressing...",
        "model": "gpt-4"
    },
    "media_relations": {
        "title": "Media Relations",
        "description": "Press releases and media communications",
        "placeholder": "What would you like to communicate to the media?",
        "model": "gpt-4-turbo"
    },
    "analytics_expert": {
        "title": "Analytics Expert",
        "description": "Content and sentiment analysis",
        "placeholder": "What would you like me to analyze?",
        "model": "claude-3"
    },
    "visual_creator": {
        "title": "Visual Creator",
        "description": "Visual content generation and guidance",
        "placeholder": "Describe the visual content you need...",
        "model": "dall-e-3"
    }
} 