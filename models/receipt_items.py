from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db import Base


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("goods.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_sale = Column(Float(precision=2), nullable=False)

    receipt = relationship("Receipt", back_populates="items")
    product = relationship("Article", back_populates="receipt_items")
