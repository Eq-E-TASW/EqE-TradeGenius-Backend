from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.services.trading_service.trading_logic import get_assets_logic, execute_trade_logic
from pydantic import BaseModel

router = APIRouter()


class TradeRequest(BaseModel):
    user_id: int
    symbol: str
    quantity: int  # Cantidad positiva para compra, negativa para venta


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/get_assets/{user_id}")
def get_assets(user_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los activos del usuario con sus precios actualizados.
    """
    try:
        return get_assets_logic(user_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/trade")
def execute_trade(trade: TradeRequest, db: Session = Depends(get_db)):
    """
    Ejecuta una operación de compra o venta de activos.
    """
    try:
        return execute_trade_logic(trade.user_id, trade.symbol, trade.quantity, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
