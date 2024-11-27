from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.services.prediction_service.lstm import predict_with_lstm
from app.services.prediction_service.svm import predict_with_svm
from app.core.utility import plot_predictions


def predict_and_log(ticker: str, model: str, db: Session):
    try:
        if model.lower() == "lstm":
            real_values, predicted_values = predict_with_lstm(ticker, db)
        elif model.lower() == "svm":
            real_values, predicted_values = predict_with_svm(ticker, db)
        else:
            raise HTTPException(status_code=400, detail="Modelo no válido. Use 'lstm' o 'svm'.")

        image_path = plot_predictions(real_values, predicted_values, ticker, model)

        return {
            "message": "Predicción realizada con éxito.",
            "real_values": real_values.tolist(),
            "predicted_values": predicted_values.tolist(),
            "image_url": f"/images/{image_path.split('/')[-1]}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
