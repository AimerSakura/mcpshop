from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.db.session import get_db
from mcpshop.crud.cart import add_to_cart, remove_cart_item, get_cart_items, clear_cart
from mcpshop.schemas.cart import CartItemCreate, CartItemOut
from mcpshop.api.deps import get_current_user

router = APIRouter(prefix="/api/cart", tags=["cart"])

@router.post("/", response_model=CartItemOut)
async def add_item(
    item: CartItemCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await add_to_cart(db, user.user_id, item.sku, item.quantity)

@router.get("/", response_model=List[CartItemOut])
async def list_cart(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_cart_items(db, user.user_id)

@router.delete("/clear", status_code=204)
async def clear_user_cart(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await clear_cart(db, user.user_id)

@router.delete("/{cart_item_id}", status_code=204)
async def delete_item(
    cart_item_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 可验证归属
    await remove_cart_item(db, cart_item_id)

