from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from mcpshop.models.cart_item import CartItem
from mcpshop.models.product import Product                 # ✅ 用于库存校验
from mcpshop.schemas.cart import CartItemCreate

async def add_to_cart(db: AsyncSession, user_id: int, sku: str, quantity: int = 1) -> CartItem:
    # ✅ 校验商品存在 & 库存充足
    prod = await db.get(Product, sku)
    if not prod or prod.stock < quantity:
        raise ValueError("商品不存在或库存不足")

    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.sku == sku)
    )
    item = result.scalars().first()
    if item:
        if prod.stock < item.quantity + quantity:
            raise ValueError("库存不足")
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, sku=sku, quantity=quantity)
        db.add(item)

    await db.commit()
    await db.refresh(item)
    return item


async def remove_cart_item(db: AsyncSession, cart_item_id: int) -> None:
    stmt = select(CartItem).where(CartItem.cart_item_id == cart_item_id)
    result = await db.execute(stmt)
    item = result.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()

async def get_cart_items(db: AsyncSession, user_id: int) -> list[CartItem]:
    result = await db.execute(select(CartItem).where(CartItem.user_id == user_id))
    return result.scalars().all()

async def clear_cart(db: AsyncSession, user_id: int) -> None:
    items = await get_cart_items(db, user_id)
    for item in items:
        await db.delete(item)
    await db.commit()