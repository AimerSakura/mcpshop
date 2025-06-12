from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from mcpshop.models.order import Order
from mcpshop.models.order_item import OrderItem
from mcpshop.models.product import Product

async def create_order(db: AsyncSession, user_id: int, items: list[dict]) -> Order:
    total = 0
    order = Order(user_id=user_id, total_cents=0)
    db.add(order)
    await db.flush()                      # 先拿到 order_id

    for it in items:
        prod: Product = await db.get(Product, it["sku"], with_for_update=True)  # ✅ 行锁保证并发安全
        if not prod:
            raise ValueError(f"商品 {it['sku']} 不存在")
        qty = it["quantity"]
        if prod.stock < qty:
            raise ValueError(f"商品 {prod.sku} 库存不足")
        total += prod.price_cents * qty
        db.add(OrderItem(
            order_id=order.order_id,
            sku=prod.sku,
            quantity=qty,
            unit_price=prod.price_cents
        ))
        prod.stock -= qty

    order.total_cents = total
    await db.commit()
    await db.refresh(order, ["items"])     # ✅ 提前加载 items，避免懒加载失败
    return order

async def get_orders_by_user(db: AsyncSession, user_id: int) -> List[Order]:
    result = await db.execute(
        select(Order).options(selectinload(Order.items))   # ✅ 解决 MissingGreenlet
        .where(Order.user_id == user_id)
    )
    return result.scalars().all()
