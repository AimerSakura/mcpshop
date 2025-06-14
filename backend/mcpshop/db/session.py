# backend/mcpshop/db/session.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from mcpshop.core.config import settings

# 1. 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
)

# 2. 创建 sessionmaker
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 3. 依赖函数：直接 yield AsyncSession
async def get_db() -> AsyncSession:
    """
    Yield 一个 AsyncSession，并在使用完后自动关闭连接。
    用法：
        async def endpoint(db: AsyncSession = Depends(get_db)):
            await db.execute(...)
    """
    async with AsyncSessionLocal() as session:
        yield session
