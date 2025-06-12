from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")