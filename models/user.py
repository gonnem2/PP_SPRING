from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from backend.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(20))
    last_name = Column(String(30))
    username = Column(String(50), unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_owner = Column(Boolean, default=False)
    is_seller = Column(Boolean, default=True)
    is_warehouse_worker = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    sales = relationship("Sales", back_populates="user")
    seller_stats = relationship("SellerStat", back_populates="users")
    receipts = relationship("Receipt", back_populates="user")
