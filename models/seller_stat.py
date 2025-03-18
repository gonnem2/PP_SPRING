from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime

from sqlalchemy.orm import relationship

from backend.db import Base


class SellerStat(Base):
    __tablename__ = "seller_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_sales = Column(Integer)
    total_amount = Column(Float)
    period = Column(DateTime)

    users = relationship("User", back_populates="seller_stats")
