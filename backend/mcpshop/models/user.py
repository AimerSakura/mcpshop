# 文件：backend/mcpshop/models/user.py
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    # —— 新增管理员标识字段 ——
    is_admin = Column(Boolean, nullable=False, server_default="false")
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    cart_items    = relationship("CartItem",      back_populates="user", cascade="all, delete-orphan")
    orders        = relationship("Order",         back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation",  back_populates="user", cascade="all, delete-orphan")
