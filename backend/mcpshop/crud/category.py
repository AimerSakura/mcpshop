from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mcpshop.models.category import Category
from mcpshop.schemas.category import CategoryCreate

async def create_category(db: AsyncSession, cat_in: CategoryCreate) -> Category:
    cat = Category(name=cat_in.name)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat

async def get_category(db: AsyncSession, category_id: int) -> Category | None:
    result = await db.execute(select(Category).where(Category.category_id == category_id))
    return result.scalars().first()

async def list_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category))
    return result.scalars().all()