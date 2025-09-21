from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
import os
import json

# 🔑 Cargar variables de entorno desde .env
load_dotenv()

app = FastAPI()

# 🔓 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # puedes restringir si quieres (ej: ["http://localhost:5500"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 API Key de OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class InputText(BaseModel):
    text: str

@app.post("/ia")
async def ia_response(data: InputText):
    """
    Endpoint que recibe texto del usuario y devuelve
    una lista de tareas en formato JSON:
    [{day, month, hour, task}]
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-3.5-turbo",  # 🔄 puedes cambiar el modelo (ej: llama2, mixtral, etc.)
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Eres un asistente de calendario. "
                            "Siempre devuelves una lista en JSON válido. "
                            "Cada objeto debe tener: {day, month, hour, task}. "
                            "Ejemplo: "
                            '[{\"day\":15,\"month\":10,\"hour\":14,\"task\":\"Reunión de equipo\"}]'
                        )
                    },
                    {"role": "user", "content": data.text}
                ],
            }
        )

    # 🔎 Interpretar respuesta
    r = response.json()
    content = r["choices"][0]["message"]["content"]

    try:
        tasks = json.loads(content)  # intentar parsear JSON de la IA
    except Exception:
        # fallback: si la IA no devolvió JSON válido
        tasks = [{"day": 1, "month": 1, "hour": 12, "task": content}]

    return {"tasks": tasks}
