from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chatbot_service.chatbot_logic import save_message, get_all_messages, get_chatbot_response

router = APIRouter()

# Modelos de entrada/salida de la API
class UserMessage(BaseModel):
    message: str

class BotResponse(BaseModel):
    messages: list[dict]

@router.get("/messages", response_model=BotResponse)
def get_messages():
    """
    Endpoint para obtener el historial completo de mensajes.
    """
    messages = get_all_messages()
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found.")
    return {"messages": [{"sender": msg.sender, "message": msg.message} for msg in messages]}

@router.post("/send-message", response_model=BotResponse)
def send_message(user_message: UserMessage):
    """
    Endpoint para enviar un mensaje y obtener una respuesta del chatbot.
    """
    # Guardar mensaje del usuario
    save_message("User", user_message.message)

    # Obtener respuesta del chatbot
    bot_response = get_chatbot_response(user_message.message)

    # Guardar respuesta del bot
    save_message("Bot", bot_response)

    # Devolver historial actualizado
    updated_messages = get_all_messages()
    return {"messages": [{"sender": msg.sender, "message": msg.message} for msg in updated_messages]}
