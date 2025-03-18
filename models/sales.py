from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime

from sqlalchemy.orm import relationship

from backend.db import Base


class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    good_id = Column(Integer, ForeignKey("goods.id"))
    quantity = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float)
    sales_date = Column(DateTime, default=datetime.now)

    users = relationship("User", back_populates="sales")
    goods = relationship("Article", back_populates="sales")
