from backend.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, DateTime
from datetime import datetime

from sqlalchemy.orm import relationship


class Article(Base):
    __tablename__ = "goods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(DECIMAL)
    cost_price = Column(DECIMAL)
    stock_quantity = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

    category = relationship("Category", back_populates="articles")
    sales = relationship("Sales", back_populates="goods")
    purchases = relationship("Purchase", back_populates="goods")
    notifications = relationship("Notification", back_populates="goods")
    good_stats = relationship("GoodStat", back_populates="goods")
    receipt_items = relationship("ReceiptItem", back_populates="product")
