from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import os

app = FastAPI()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Load system prompt
with open("prompt.txt", "r") as f:
    SYSTEM_PROMPT = f.read()

# Simple in-memory chat history
chat_memory = []

class Question(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/ask")
def ask_ai(data: Question):
    global chat_memory

    # Add user message
    chat_memory.append({"role": "user", "content": data.question})

    # Keep only last 6 messages
    chat_memory = chat_memory[-6:]

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                *chat_memory
            ]
        }
    )

    ai_reply = response.json()["choices"][0]["message"]["content"]

    chat_memory.append({"role": "assistant", "content": ai_reply})

    return {"reply": ai_reply}
