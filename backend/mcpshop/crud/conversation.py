from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mcpshop.models.conversation import Conversation

async def create_conversation(db: AsyncSession, user_id: int, session_id: str) -> Conversation:
    conv = Conversation(user_id=user_id, session_id=session_id)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv

async def get_conversation(db: AsyncSession, conv_id: int) -> Conversation | None:
    result = await db.execute(select(Conversation).where(Conversation.conv_id == conv_id))
    return result.scalars().first()
