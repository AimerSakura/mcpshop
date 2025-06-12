from sqlalchemy import Column, BigInteger, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.order_id"), nullable=False)
    sku = Column(String(32), ForeignKey("products.sku"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")