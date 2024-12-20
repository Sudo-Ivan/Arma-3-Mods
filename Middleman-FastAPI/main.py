from fastapi import FastAPI, HTTPException
from models import ChatRequest, ChatResponse
from config import settings
from logger import logger
import requests

app = FastAPI()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.debug(f"Received request: {request}")

    if request.provider == "openrouter":
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "HTTP-Referer": settings.openrouter_site_url,
                    "X-Title": settings.openrouter_site_name,
                    "Content-Type": "application/json",
                },
                json={
                    "model": request.model,
                    "messages": [msg.dict() for msg in request.messages],
                },
            )
            logger.debug(f"OpenRouter raw response: {response.text}")
            result = response.json()
            return ChatResponse(
                response=result["choices"][0]["message"]["content"],
                provider="openrouter",
            )
        except Exception as e:
            logger.error(f"OpenRouter error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    elif request.provider == "ollama":
        try:
            response = requests.post(
                f"{settings.ollama_api_url}/api/generate",
                json={
                    "model": "llama3.2:latest",
                    "prompt": request.messages[-1].content,
                    "temperature": request.temperature,
                    "stream": False,
                },
            )
            logger.debug(f"Ollama raw response: {response.text}")
            result = response.json()
            return ChatResponse(response=result["response"], provider="ollama")
        except Exception as e:
            logger.error(f"Ollama error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    raise HTTPException(status_code=400, detail="Invalid provider specified")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
