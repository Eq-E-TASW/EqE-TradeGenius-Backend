import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuraciones generales
    APP_NAME: str = "TradeGenius Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development | production

    # Configuración de base de datos
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")  # URL de la BD

    # Configuración del chatbot (API de OpenAI)
    OPEN_AI_API_KEY: str = os.getenv("OPEN_AI_API_KEY", "test")

    # Configuración del servidor
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8000))

    class Config:
        env_file = ".env"  # Archivo donde se definen las variables de entorno

# Instancia global de configuración
settings = Settings()
