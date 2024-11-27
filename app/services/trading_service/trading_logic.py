from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import UserAssets, TradingHistory, HistoricalData


def update_current_prices(db: Session):
    """
    Actualiza el precio actual de cada activo en UserAssets basado en el último precio de cierre de HistoricalData.
    """
    user_assets = db.query(UserAssets).all()

    for asset in user_assets:
        latest_price_entry = db.query(HistoricalData).filter(
            HistoricalData.symbol == asset.symbol
        ).order_by(desc(HistoricalData.date)).first()

        if latest_price_entry:
            asset.current_price = latest_price_entry.close

    db.commit()
    return {"message": "Precios actualizados correctamente"}


def get_assets_logic(user_id: int, db: Session):
    """
    Obtiene los activos del usuario, actualiza sus precios y calcula el valor total de los activos.
    """
    update_current_prices(db)

    user_assets = db.query(UserAssets).filter(UserAssets.user_id == user_id).all()

    if not user_assets:
        raise ValueError("No se encontraron activos para este usuario.")

    assets_data = []
    total_value = 0

    for asset in user_assets:
        subtotal = asset.quantity * asset.current_price
        total_value += subtotal
        assets_data.append({
            "Nombre": asset.symbol,
            "Cantidad": asset.quantity,
            "P. Unit.": asset.current_price,
            "Subtotal": subtotal
        })

    return {
        "Assets": assets_data,
        "Total": total_value
    }


def execute_trade_logic(user_id: int, symbol: str, quantity: int, db: Session):
    """
    Ejecuta una operación de compra o venta de activos y actualiza las tablas UserAssets y TradingHistory.
    """
    latest_price_entry = db.query(HistoricalData).filter(
        HistoricalData.symbol == symbol
    ).order_by(desc(HistoricalData.date)).first()

    if not latest_price_entry:
        raise ValueError("Acción no válida")

    buy_price = latest_price_entry.close

    asset = db.query(UserAssets).filter(
        UserAssets.user_id == user_id,
        UserAssets.symbol == symbol
    ).first()

    if not asset:
        if quantity < 0:
            raise ValueError("No tienes suficientes acciones para vender.")
        asset = UserAssets(
            user_id=user_id,
            symbol=symbol,
            quantity=quantity,
            current_price=buy_price
        )
        db.add(asset)
    else:
        if quantity < 0 and abs(quantity) > asset.quantity:
            raise ValueError("No tienes suficientes acciones para vender.")

        new_quantity = asset.quantity + quantity
        new_price = asset.current_price

        if quantity > 0:
            total_cost = (asset.quantity * asset.current_price) + (quantity * buy_price)
            new_price = total_cost / new_quantity

        asset.quantity = new_quantity
        asset.current_price = new_price

    trade_history = TradingHistory(
        user_id=user_id,
        symbol=symbol,
        quantity=quantity,
        buy_price=buy_price
    )
    db.add(trade_history)
    db.commit()

    return {"message": "Operación exitosa! Datos actualizados"}
