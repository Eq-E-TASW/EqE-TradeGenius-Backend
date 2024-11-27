from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    UniqueConstraint,
)
from datetime import datetime
from app.models.database import Base

# Modelo: HistoricalData
class HistoricalData(Base):
    __tablename__ = "historical_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    date = Column(DateTime, index=True)

    # Evita que el mismo símbolo con la misma fecha se repita
    __table_args__ = (UniqueConstraint('symbol', 'date', name='_symbol_date_uc'),)

    def __repr__(self):
        return f"<HistoricalData(symbol={self.symbol}, date={self.date})>"

# Modelo: PredictionLog
class PredictionLog(Base):
    __tablename__ = "prediction_log"

    id = Column(Integer, primary_key=True, index=True)
    prediction_time = Column(DateTime, default=datetime.utcnow, index=True)
    ticker = Column(String, index=True)
    model_used = Column(String, index=True)
    predicted_date = Column(DateTime, index=True)
    predicted_close_price = Column(Float)

    def __repr__(self):
        return (
            f"<PredictionLog(ticker={self.ticker}, model={self.model_used}, "
            f"date={self.predicted_date}, price={self.predicted_close_price})>"
        )

# Modelo: UserAssets
class UserAssets(Base):
    __tablename__ = 'user_assets'

    user_id = Column(Integer, primary_key=True)
    symbol = Column(String, primary_key=True)  # Clave primaria compuesta
    quantity = Column(Integer, nullable=False)
    current_price = Column(Float, nullable=False)

    def __repr__(self):
        return (
            f"<UserAssets(user_id={self.user_id}, symbol='{self.symbol}', "
            f"quantity={self.quantity}, current_price={self.current_price})>"
        )

# Modelo: TradingHistory
class TradingHistory(Base):
    __tablename__ = 'trading_history'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Identificador único
    user_id = Column(Integer, nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)  # Positivo para compras, negativo para ventas
    buy_price = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<TradingHistory(id={self.id}, user_id={self.user_id}, symbol='{self.symbol}', "
            f"quantity={self.quantity}, buy_price={self.buy_price}, date={self.date})>"
        )

# Modelo: Message (Chatbot History)
class Message(Base):
    __tablename__ = "chatbot_history"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Message(sender={self.sender}, created_at={self.created_at})>"
