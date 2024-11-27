import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, desc
from app.models.models import HistoricalData
import requests


# Obtener rango de fechas
def get_date_range(amount: int, unit: str):
    today = datetime.today()
    if unit == "days":
        start_date = today - timedelta(days=amount)
    elif unit == "weeks":
        start_date = today - timedelta(weeks=amount)
    elif unit == "months":
        start_date = today - timedelta(days=30 * amount)
    elif unit == "years":
        start_date = today - timedelta(days=365 * amount)
    else:
        raise ValueError("Unidad de tiempo no válida. Use 'days', 'weeks', 'months', o 'years'.")
    return start_date, today


# Obtener datos históricos de Binance
def get_historical_crypto_data_binance(symbol: str, start_date: str, end_date: str):
    url = "https://api.binance.com/api/v3/klines"
    start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
    end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
    params = {
        "symbol": symbol.upper() + "USDT",
        "interval": "1d",
        "startTime": start_timestamp,
        "endTime": end_timestamp,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Error al obtener datos de Binance: {response.status_code}")
    return response.json()


# Guardar datos históricos en la base de datos
def save_historical_data(db: Session, symbol: str, asset_type: str, data: pd.DataFrame):
    for _, row in data.iterrows():
        historical_data = HistoricalData(
            symbol=symbol,
            date=row.name,
            open=row["Open"],
            high=row["High"],
            low=row["Low"],
            close=row["Close"],
            volume=row["Volume"],
        )
        db.add(historical_data)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()


# Generar gráfico de precios
def generate_price_plot(db: Session, tickers: list, start_date, end_date, price_type: str, unit: str, amount: int):
    plt.figure(figsize=(10, 6))

    # Si solo hay un ticker, usar sombreado
    if len(tickers) == 1:
        ticker = tickers[0]

        # Consultar los datos de la base de datos para el único ticker
        data = db.query(HistoricalData.date, getattr(HistoricalData, price_type)).filter(
            and_(
                HistoricalData.symbol == ticker,
                HistoricalData.date >= start_date,
                HistoricalData.date <= end_date
            )
        ).order_by(HistoricalData.date).all()

        if not data:
            raise ValueError("No se encontraron datos para el ticker y rango de tiempo especificados.")

        # Extraer datos de fechas y precios
        dates = [entry.date for entry in data]
        prices = [getattr(entry, price_type) for entry in data]
        min_valor = min(prices)

        # Obtener el último valor y el valor pico
        last_value = prices[-1]
        peak_value = max(prices)

        last_date = dates[-1]
        peak_date = dates[prices.index(peak_value)]

        # Trazar la línea para el único ticker con sombreado
        plt.plot(dates, prices, color="blue", label=ticker)
        plt.fill_between(dates, prices, min_valor, color="lightblue", alpha=0.4)

        # Ajustar la posición de las anotaciones
        if unit == "years" and amount == 1:
            xytext_last = (last_date, last_value + 6)
            xytext_peak = (peak_date - timedelta(days=30), peak_value + 6) if abs((peak_date - last_date).days) <= 2 else (peak_date, peak_value + 6)
        elif unit == "months" and amount == 6:
            xytext_last = (last_date, last_value + 6)
            xytext_peak = (peak_date - timedelta(days=15), peak_value + 6) if abs((peak_date - last_date).days) <= 2 else (peak_date, peak_value + 6)
        elif unit == "months" and amount == 1:
            xytext_last = (last_date, last_value + 2)
            xytext_peak = (peak_date - timedelta(days=2), peak_value + 2) if abs((peak_date - last_date).days) <= 1 else (peak_date, peak_value + 2)
        elif unit == "weeks" and amount == 1:
            xytext_last = (last_date, last_value + 0.5)
            xytext_peak = (peak_date - timedelta(hours=12), peak_value + 0.5) if abs((peak_date - last_date).days) == 0 else (peak_date, peak_value + 0.5)
        else:
            xytext_last = (last_date, last_value + 6)
            xytext_peak = (peak_date, peak_value + 6)

        # Anotación para el último valor
        plt.annotate(
            f'{last_value:.1f}',
            xy=(last_date, last_value),
            xytext=xytext_last,
            fontsize=11,
            color='red',
            ha='center',
            va='center',
            fontweight='semibold',
            arrowprops=dict(facecolor='red', arrowstyle='->')
        )

        # Anotación para el valor pico
        plt.annotate(
            f'{peak_value:.1f}',
            xy=(peak_date, peak_value),
            xytext=xytext_peak,
            fontsize=11,
            color='black',
            ha='center',
            va='bottom',
            fontweight='semibold',
            arrowprops=dict(facecolor='black', arrowstyle='->')
        )

    else:
        # Si hay más de un ticker, graficar sin sombreado
        colors = ["blue", "green", "red", "orange", "purple"]
        for idx, ticker in enumerate(tickers):
            data = db.query(HistoricalData.date, getattr(HistoricalData, price_type)).filter(
                and_(
                    HistoricalData.symbol == ticker,
                    HistoricalData.date >= start_date,
                    HistoricalData.date <= end_date
                )
            ).order_by(HistoricalData.date).all()

            if not data:
                continue

            dates = [entry.date for entry in data]
            prices = [getattr(entry, price_type) for entry in data]

            last_value = prices[-1]
            peak_value = max(prices)  
    
            last_date = dates[-1]
            peak_date = dates[prices.index(peak_value)]

            # Trazar la línea para cada ticker sin sombreado
            plt.plot(dates, prices, color=colors[idx % len(colors)], label=ticker)
            plt.fill_between(dates, prices, color=colors[idx % len(colors)], alpha=0.1)

            if unit == "years" and amount == 1: 
                xytext_last = (last_date, last_value + 20)
                if (abs((peak_date - last_date).days) <= 20):
                    xytext_peak = (peak_date - timedelta(days=30), peak_value + 6)
                else:
                    xytext_peak = (peak_date, peak_value + 10)
            elif unit == "months" and amount == 6:
                xytext_last = (last_date, last_value + 20)
                if (abs((peak_date - last_date).days) <= 3):
                    xytext_peak = (peak_date - timedelta(days=15), peak_value + 6)
                else:
                    xytext_peak = (peak_date, peak_value + 10)
            elif unit == "months" and amount == 1:
                xytext_last = (last_date, last_value + 20)
                if (abs((peak_date - last_date).days) <= 1):
                    xytext_peak = (peak_date - timedelta(days=2), peak_value + 6)
                else:
                    xytext_peak = (peak_date, peak_value + 10)
            elif unit == "weeks" and amount == 1:
                xytext_last = (last_date, last_value + 20)
                if (abs((peak_date - last_date).days) == 0):
                    xytext_peak = (peak_date - timedelta(hours=12), peak_value + 6)
                else:
                    xytext_peak = (peak_date, peak_value + 0.5)
            else:
                xytext_last = (last_date, last_value + 6)
                xytext_peak = (peak_date, peak_value + 6)


            # Anotación para el último valor
            plt.annotate(
                f'{last_value:.1f}', 
                xy=(last_date, last_value), 
                xytext=xytext_last,  # Ajusta la posición del texto
                fontsize=11, 
                color='red', 
                ha='center', 
                va='center', 
                fontweight='semibold',
                arrowprops=dict(facecolor='red', arrowstyle='->')
            )

            # Anotación para el valor pico
            plt.annotate(
                f'{peak_value:.1f}', 
                xy=(peak_date, peak_value), 
                xytext=xytext_peak,  # Ajusta la posición del texto
                fontsize=11, 
                color='black', 
                ha='center', 
                va='bottom', 
                fontweight='semibold',
                arrowprops=dict(facecolor='black', arrowstyle='->')
            )

        plt.legend(title="Ticker", bbox_to_anchor=(0.5, 1.01), loc='lower center', ncol=len(tickers))

    # Configurar el gráfico
    plt.ylabel(f"Precio ({price_type.capitalize()})")
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)

    # Guardar el gráfico en un buffer
    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf


# Generar gráfico de volumen
def generate_volume_plot(db: Session, tickers: list):
    plt.figure(figsize=(10, 6))
    colors = ["blue", "green", "red", "orange", "purple"]
    volumes = []
    valid_tickers = []

    for ticker in tickers:
        result = db.query(HistoricalData.volume, HistoricalData.date).filter(
            HistoricalData.symbol == ticker
        ).order_by(HistoricalData.date.desc()).first()

        if result:
            volumes.append(result.volume)
            valid_tickers.append(ticker)

    if not valid_tickers:
        raise ValueError("No se encontraron datos para los tickers seleccionados.")

    bars = plt.bar(valid_tickers, volumes, color=colors[:len(valid_tickers)])

    for bar, volume in zip(bars, volumes):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{volume}", ha="center")

    plt.xlabel("Tickers")
    plt.ylabel("Volumen")
    plt.xticks(rotation=45)
    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)

    buff = BytesIO()
    plt.savefig(buff, format="png")
    buff.seek(0)
    plt.close()
    return buff
