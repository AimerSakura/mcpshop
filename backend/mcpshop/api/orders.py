from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.db.session import get_db
from mcpshop.crud.cart import get_cart_items, clear_cart  # ✅ 补齐缺失 import
from mcpshop.crud.order import create_order, get_orders_by_user
from mcpshop.api.deps import get_current_user
from mcpshop.schemas.order import OrderOut

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/", response_model=OrderOut)
async def place_order(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    items = await get_cart_items(db, user.user_id)
    if not items:
        raise HTTPException(status_code=400, detail="购物车为空")

    # 构造订单明细
    details = [{"sku": i.sku, "quantity": i.quantity} for i in items]
    order = await create_order(db, user.user_id, details)

    # 下单成功后清空购物车
    await clear_cart(db, user.user_id)
    return order

@router.get("/", response_model=List[OrderOut])
async def list_orders(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_orders_by_user(db, user.user_id)
