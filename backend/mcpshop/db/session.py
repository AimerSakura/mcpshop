# mcpshop/db/session.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from mcpshop.core.config import settings

# 1. 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,  # 格式示例：mysql+asyncmy://user:pass@host:3306/dbname
    echo=True,  # 是否打印 SQL 到控制台，开发时可开，生产可关
    future=True  # 使用 2.0 风格 API
)

# 2. 创建 sessionmaker，用于产生 AsyncSession
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # 提交后不 expire 对象，便于后续访问属性
)


# 3. 依赖注入函数：在 FastAPI 路由中使用 Depends(get_db)
async def get_db() -> AsyncSession:
    """
    Yield 一个 AsyncSession，并在使用完后自动关闭连接。
    用法示例：
        @router.get("/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(...)
    """
    async with AsyncSessionLocal() as session:
        yield session
