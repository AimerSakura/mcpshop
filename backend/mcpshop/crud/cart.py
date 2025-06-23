from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from mcpshop.models.cart_item import CartItem
from mcpshop.models.product import Product

async def add_to_cart(db: AsyncSession, user_id: int, sku: str, quantity: int = 1) -> CartItem:
    # 校验商品存在 & 库存充足
    prod = await db.get(Product, sku)
    if not prod or prod.stock < quantity:
        raise HTTPException(status_code=400, detail="商品不存在或库存不足")

    # 查询购物车中是否已存在该商品
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.sku == sku)
    )
    item = result.scalars().first()
    if item:
        # 合并数量并校验库存
        if prod.stock < item.quantity + quantity:
            raise HTTPException(status_code=400, detail="库存不足")
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, sku=sku, quantity=quantity)
        db.add(item)

    # 提交事务并预加载关联的 product
    await db.commit()
    await db.refresh(item)
    await db.refresh(item, ["product"])
    return item

async def remove_cart_item(db: AsyncSession, cart_item_id: int) -> None:
    # 删除指定购物项
    result = await db.execute(
        select(CartItem).where(CartItem.cart_item_id == cart_item_id)
    )
    item = result.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()

async def get_cart_items(db: AsyncSession, user_id: int) -> list[CartItem]:
    # 查询并预加载关联的 product，避免懒加载错误
    result = await db.execute(
        select(CartItem)
          .options(selectinload(CartItem.product))
          .where(CartItem.user_id == user_id)
    )
    return result.scalars().all()

async def clear_cart(db: AsyncSession, user_id: int) -> None:
    # 清空购物车
    items = await get_cart_items(db, user_id)
    for item in items:
        await db.delete(item)
    await db.commit()
