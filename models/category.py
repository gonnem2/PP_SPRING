from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from backend.db import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )
    title = Column(String, unique=True)

    articles = relationship("Article", back_populates="category", cascade="all, delete")
    parent = relationship(
        "Category", remote_side=[id], backref="children", cascade="all, delete"
    )
