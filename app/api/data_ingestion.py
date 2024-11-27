from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.services.data_ingestion_service.ingestion_logic import (
    get_date_range,
    get_historical_crypto_data_binance,
    save_historical_data,
    generate_price_plot,
    generate_volume_plot,
)
from app.models.models import HistoricalData
from sqlalchemy import desc, func, and_
from fastapi.responses import StreamingResponse
from typing import List
import yfinance as yf
import io
import pandas as pd

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/historical-data/")
def get_historical_data(
    ticker: str,
    amount: int = 1,
    unit: str = "years",
    asset_type: str = "stock",
    db: Session = Depends(get_db),
):
    try:
        start_date, end_date = get_date_range(amount, unit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if asset_type == "stock":
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        except Exception:
            raise HTTPException(status_code=500, detail="Error al obtener datos financieros")
        if data.empty:
            raise HTTPException(status_code=404, detail="Datos no encontrados para el ticker especificado")
        save_historical_data(db, ticker, "stock", data)
        stream = io.StringIO()
        data.to_csv(stream)

    elif asset_type == "crypto":
        data = get_historical_crypto_data_binance(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if not data:
            raise HTTPException(status_code=404, detail="Datos no encontrados para la criptomoneda especificada")
        df = pd.DataFrame(data, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
        df.rename(columns={'Open Time': 'Date'}, inplace=True)
        df.set_index('Date', inplace=True)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        save_historical_data(db, ticker, "crypto", df)
        stream = io.StringIO()
        df.to_csv(stream)
    else:
        raise HTTPException(status_code=400, detail="Tipo de activo no válido. Use 'stock' o 'crypto'.")

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={ticker}_historical_data_{amount}_{unit}.csv"
    return response


@router.get("/tickers")
def get_tickers(
    all: bool = Query(False, description="Colocar True para mostrar todos los tickers"),
    db: Session = Depends(get_db),
):
    try:
        # Subconsulta para obtener el último registro de cada símbolo
        subquery = (
            db.query(
                HistoricalData.symbol,
                func.max(HistoricalData.date).label("latest_date")
            )
            .group_by(HistoricalData.symbol)
            .subquery()
        )

        # Unimos la tabla con la subconsulta para obtener el precio más reciente
        query = (
            db.query(HistoricalData)
            .join(subquery, and_(
                HistoricalData.symbol == subquery.c.symbol,
                HistoricalData.date == subquery.c.latest_date
            ))
            .order_by(desc(HistoricalData.close))
        )

        # Limita a 5 resultados si "all" es False, de lo contrario trae todos
        if not all:
            query = query.limit(5)

        latest_prices = query.all()

        data = []
        for record in latest_prices:
            # Obtiene el registro anterior al último para calcular el cambio
            previous_record = (
                db.query(HistoricalData)
                .filter(
                    HistoricalData.symbol == record.symbol,
                    HistoricalData.date < record.date
                )
                .order_by(desc(HistoricalData.date))
                .first()
            )

            # Verifica si existe un registro anterior para calcular el cambio
            if previous_record:
                change = round(record.close - previous_record.close, 2)
                trendup = change > 0
            else:
                change = 0.0
                trendup = None

            # Redondea el precio a dos decimales y obtiene el nombre completo
            price = round(record.close, 2)
            company_name = record.symbol  # Aquí puedes usar get_company_name si quieres agregar nombres

            # Agrega los datos al resultado
            data.append({
                "name": company_name,
                "price": price,
                "change": change,
                "trendup": trendup
            })

        return data

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


@router.get("/plot/")
def plot_price(
    tickers: List[str] = Query(...),
    amount: int = 1,
    unit: str = "years",
    price_type: str = "close",
    db: Session = Depends(get_db),
):
    try:
        start_date, end_date = get_date_range(amount, unit)
        buf = generate_price_plot(db, tickers, start_date, end_date, price_type, unit, amount)
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plot_last_volume")
def plot_last_volume(
    tickers: List[str] = Query(...),
    db: Session = Depends(get_db),
):
    try:
        buf = generate_volume_plot(db, tickers)
        return StreamingResponse(buf, media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
