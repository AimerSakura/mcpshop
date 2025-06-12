# app/schemas/cart.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CartItemBase(BaseModel):
    sku: str
    quantity: int = Field(..., ge=1)

class CartItemCreate(CartItemBase):
    ...

class CartItemOut(CartItemBase):
    cart_item_id: int
    added_at: datetime
    # 嵌套商品简略信息
    product: Optional[dict]

    class Config:
        orm_mode = True
