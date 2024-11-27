from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from tavily import TavilyClient
from pydantic import BaseModel
import json
import openai
from app.core.config import settings

tavily_client = TavilyClient(api_key="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")

openai.api_key = settings.OPEN_AI_API_KEY

class SentimentAnalysisResult(BaseModel):
    titular: str
    sentimiento: str
    puntaje: float
    explicacion: str

class AnalysisResponse(BaseModel):
    analisis: List[SentimentAnalysisResult]

def get_news_from_tavily(query: str, max_results: int) -> List[str]:
    try:
        search_results = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        return [result.get('title') for result in search_results['results'] if 'title' in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Tavily: {str(e)}")

# Función para analizar sentimientos
def analyze_sentiment(headlines: List[str]) -> AnalysisResponse:
    if not headlines:
        return {"analisis": []}
    
    analysis_prompt = f"""Analiza el sentimiento de los siguientes titulares y clasifícalos como positivo, negativo o neutral. 
    Además, proporciona un puntaje de -1 (muy negativo) a 1 (muy positivo).
    
    Titulares: {headlines}
    
    Responde en formato JSON con la siguiente estructura:
    {{
        "analisis": [
            {{
                "titular": "texto del titular",
                "sentimiento": "positivo/negativo/neutral",
                "puntaje": float,
                "explicacion": "breve explicación del análisis"
            }}
        ]
    }}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"}
        )
        return AnalysisResponse(**json.loads(response.choices[0].message.content))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en OpenAI: {str(e)}")