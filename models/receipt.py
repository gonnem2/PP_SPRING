from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    closed_at = Column(DateTime, nullable=True)
    total_amount = Column(Float(precision=2), default=0.0)
    status = Column(String(20), default="open")

    user = relationship("User", back_populates="receipts")
    items = relationship(
        "ReceiptItem", back_populates="cash", cascade="all, delete-orphan"
    )
    sales = relationship("Sales", back_populates="receipt")
