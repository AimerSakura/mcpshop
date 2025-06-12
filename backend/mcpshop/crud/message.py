from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from mcpshop.models.message import Message, Sender          # ✅ 引入枚举
from mcpshop.schemas.chat import MessageIn

async def add_message(db: AsyncSession, conv_id: int, sender: str, content: str) -> Message:
    msg = Message(conv_id=conv_id, sender=Sender(sender), content=content)  # ✅ 枚举化
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def get_messages(db: AsyncSession, conv_id: int) -> list[Message]:
    result = await db.execute(select(Message).where(Message.conv_id == conv_id).order_by(Message.created_at))
    return result.scalars().all()
