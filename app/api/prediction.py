from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.services.prediction_service.prediction_logic import predict_and_log
import os
from fastapi.responses import FileResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/predict/")
def predict_and_log_endpoint(ticker: str, model: str, db: Session = Depends(get_db)):
    """
    Realiza predicciones usando LSTM o SVM, almacena la gráfica y retorna la información.
    """
    try:
        return predict_and_log(ticker, model, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{filename}")
def get_image(filename: str):
    """
    Endpoint para obtener una imagen almacenada.
    """
    file_path = os.path.join("images", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
