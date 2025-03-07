from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)

    articles = relationship("Article", back_populates="category")

