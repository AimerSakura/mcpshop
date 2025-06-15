from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.db.session import get_db
from mcpshop.crud.cart import get_cart_items, clear_cart
from mcpshop.crud.order import create_order, get_orders_by_user
from mcpshop.api.deps import get_current_user, get_current_admin_user
from mcpshop.schemas.order import OrderOut
from mcpshop.models.order import Order

router = APIRouter(prefix="/api/orders", tags=["orders"])

# 普通用户下单
@router.post("/", response_model=OrderOut)
async def place_order(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    items = await get_cart_items(db, user.user_id)
    if not items:
        raise HTTPException(status_code=400, detail="购物车为空")
    details = [{"sku": i.sku, "quantity": i.quantity} for i in items]
    order = await create_order(db, user.user_id, details)
    await clear_cart(db, user.user_id)
    return order

# 普通用户查自己订单
@router.get("/", response_model=List[OrderOut])
async def list_orders(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_orders_by_user(db, user.user_id)

# ★ 管理员查所有订单（管理员专属接口）
@router.get("/all", response_model=List[OrderOut], dependencies=[Depends(get_current_admin_user)])
async def list_all_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute("SELECT * FROM orders")
    return result.scalars().all()
