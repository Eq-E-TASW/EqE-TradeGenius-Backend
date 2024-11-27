from fastapi import APIRouter, Query, Depends, HTTPException
from app.models.database import SessionLocal
from app.services.sentiment_analysis.sentiment_analysis_logic import SentimentAnalysisResult, AnalysisResponse, get_news_from_tavily, analyze_sentiment

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/analyze-news", response_model=AnalysisResponse)
def analyze_news(
    query: str = Query(..., description="Tema para buscar noticias"),
    max_results: int = Query(
        5, ge=1, le=20, description="Número máximo de noticias a analizar (entre 1 y 20)"
    )
    ):

    # Obtener titulares
    headlines = get_news_from_tavily(query=query, max_results=max_results)
    if not headlines:
        raise HTTPException(status_code=404, detail="No se encontraron titulares para analizar.")
    
    # Analizar sentimientos
    results = analyze_sentiment(headlines)
    return results