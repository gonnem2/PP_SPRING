from sqlalchemy import Column, Integer, String

from sqlalchemy.orm import relationship

from backend.db import Base


class FinancialType(Base):
    __tablename__ = "financial_types"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)

    financial_records = relationship(
        "FinancialRecords", back_populates="financial_types"
    )
