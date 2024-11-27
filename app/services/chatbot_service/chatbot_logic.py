from app.models.database import SessionLocal
from app.models.models import Message
from datetime import datetime
import openai
from app.core.config import settings

# Configuración de OpenAI
openai.api_key = settings.OPEN_AI_API_KEY

def save_message(sender: str, content: str):
    """
    Guarda un mensaje en la base de datos.
    """
    db = SessionLocal()
    try:
        msg = Message(sender=sender, message=content, created_at=datetime.utcnow())
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
    finally:
        db.close()

def get_all_messages():
    """
    Obtiene todos los mensajes almacenados en la base de datos.
    """
    db = SessionLocal()
    try:
        messages = db.query(Message).order_by(Message.created_at).all()
        return messages
    finally:
        db.close()

def get_chatbot_response(user_message: str):
    """
    Obtiene una respuesta del chatbot utilizando la API de OpenAI.
    """
    # Preparar historial para la API de OpenAI
    db = SessionLocal()
    try:
        api_messages = [
            {"role": "system", "content": "Eres Finn, un asistente amigable que ayuda con información financiera y general."}
        ]
        messages = db.query(Message).order_by(Message.created_at).all()
        for msg in messages:
            role = "user" if msg.sender == "User" else "assistant"
            api_messages.append({"role": role, "content": msg.message})
    finally:
        db.close()

    # Llamada a la API de OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=api_messages
    )
    return response.choices[0].message.content
