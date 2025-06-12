from sqlalchemy import Column, BigInteger, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base
import enum

class Sender(enum.Enum):
    USER = "user"
    BOT = "bot"

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    conv_id = Column(BigInteger, ForeignKey("conversations.conv_id"), nullable=False)
    sender = Column(SQLEnum(Sender), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")
