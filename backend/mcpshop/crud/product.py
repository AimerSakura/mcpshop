# app/crud/product.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from typing import List
from mcpshop.models.product import Product
from mcpshop.schemas.product import ProductCreate

async def get_all_products(db: AsyncSession) -> List[Product]:
    result = await db.execute(select(Product))
    return result.scalars().all()

async def create_product(db: AsyncSession, p_in: ProductCreate) -> Product:
    prod = Product(
        sku=p_in.sku,
        name=p_in.name,
        price_cents=p_in.price_cents,
        stock=p_in.stock,
        description=p_in.description,
        image_url=p_in.image_url,
        category_id=p_in.category_id
    )
    db.add(prod)
    await db.commit()
    await db.refresh(prod)
    return prod

async def get_product_by_sku(db: AsyncSession, sku: str) -> Product | None:
    result = await db.execute(select(Product).where(Product.sku == sku))
    return result.scalars().first()

async def search_products(db: AsyncSession, q: str, limit: int = 20) -> List[Product]:
    stmt = select(Product).where(
        or_(Product.name.ilike(f"%{q}%"), Product.description.ilike(f"%{q}%"))
    ).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()