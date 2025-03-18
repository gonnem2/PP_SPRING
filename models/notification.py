from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime

from sqlalchemy.orm import relationship

from backend.db import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    good_id = Column(Integer, ForeignKey("goods.id"))
    description = Column(String)
    date = Column(DateTime, default=datetime.now)

    goods = relationship("Article", "notifications")
