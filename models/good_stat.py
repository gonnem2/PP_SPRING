from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime

from sqlalchemy.orm import relationship

from backend.db import Base


class GoodStat(Base):
    __tablename__ = "product_stats"

    id = Column(Integer, primary_key=True, index=True)
    good_id = Column(Integer, ForeignKey("goods.id"))
    total_sales = Column(Integer)
    amount = Column(Float)
    period = Column(DateTime)

    goods = relationship("Article", back_populates="good_stats")
