import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import HistoricalData


def plot_predictions(real_values, predicted_values, ticker, model_name):
    """
    Genera una gráfica comparativa entre los valores reales y los predichos y la almacena en una carpeta.
    """
    # Crear fechas para los valores reales (hacia atrás)
    end_date_real = pd.to_datetime('now')  # Fecha actual para los valores reales
    start_date_real = end_date_real - pd.Timedelta(days=len(real_values))  # Calcular la fecha de inicio para reales

    # Crear fechas para los valores predichos (hacia adelante)
    start_date_predicted = end_date_real  # Los predichos comienzan ahora
    end_date_predicted = start_date_predicted + pd.Timedelta(days=len(predicted_values))  # Calcular la fecha final para predicciones
    # Crear un DataFrame con los valores reales y predichos
    data_real = pd.DataFrame({
        'Fecha': pd.date_range(start=start_date_real, end=end_date_real, periods=len(real_values)),
        'Real': real_values
    })

    data_predicted = pd.DataFrame({
        'Fecha': pd.date_range(start=start_date_predicted, end=end_date_predicted, periods=len(predicted_values)),
        'Predicho': predicted_values
    })

    # Iniciar la figura
    plt.figure(figsize=(14, 7))

    # Graficar valores reales y predichos
    plt.plot(data_real['Fecha'], data_real['Real'], label="Valores Reales", color="blue", linewidth=2)
    plt.plot(data_predicted['Fecha'], data_predicted['Predicho'], label="Valores Predichos", color="orange", linewidth=2)

    # Agregar conexión entre valores reales y predichos
    plt.plot(
        [data_real['Fecha'].iloc[-1], data_predicted['Fecha'].iloc[0]],  # Fechas de conexión
        [data_real['Real'].iloc[-1], data_predicted['Predicho'].iloc[0]],  # Valores de conexión
        color='orange', linestyle='--'
    )

    # Agregar título y etiquetas
    plt.title(f"Predicción de {ticker} usando {model_name}", fontsize=16)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Precio de Cierre', fontsize=12)

    # Mostrar leyenda
    plt.legend()

    # Crear carpeta 'images' si no existe
    os.makedirs('images', exist_ok=True)

    # Guardar la imagen
    image_path = f'images/{ticker}_prediction_{model_name}.png'
    plt.savefig(image_path)
    plt.close()  # Cerrar la figura para liberar memoria

    return image_path

def get_historical_data_from_db(db: Session, ticker: str, current_date: datetime, days: int = 365):
    start_date = current_date - timedelta(days=days)
    return db.query(HistoricalData).filter(
        HistoricalData.symbol == ticker,
        HistoricalData.date >= start_date
    ).order_by(HistoricalData.date).all()