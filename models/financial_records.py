from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime

from sqlalchemy.orm import relationship

from backend.db import Base


class FinancialRecords(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    type_fin_id = Column(Integer, ForeignKey("financial_types.id"))
    amount = Column(Float)
    description = Column(String)
    date = Column(DateTime, default=datetime.now)

    financial_types = relationship("FinancialType", back_populates="financial_records")
