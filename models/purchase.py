from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime

from sqlalchemy.orm import relationship

from backend.db import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    good_id = Column(Integer, ForeignKey("goods.id"))
    quantity = Column(Integer)
    total_cost = Column(Float)
    pur_data = Column(DateTime, default=datetime.now())

    goods = relationship("Article", back_populates="purchases")
