from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import data_ingestion, prediction, trading, chatbot, sentiment
from app.core.config import settings

# Crear la instancia de la aplicación
app = FastAPI(
    title=settings.APP_NAME,
    description="API para los servicios de ingesta de datos, predicción, trading y chatbot.",
    version=settings.VERSION,
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar a dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers de los servicios
app.include_router(data_ingestion.router, prefix="/api/data_ingestion", tags=["Ingesta de Datos"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["Predicción"])
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["Sentimientos"])

# Endpoint raíz
@app.get("/", tags=["Root"])
async def root():
    return {"message": f"¡Bienvenido al backend de TradeGenius!"}

# Configuración para iniciar el servidor usando uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
