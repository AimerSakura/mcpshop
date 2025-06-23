from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from mcpshop.schemas.product import ProductOut

class CartItemBase(BaseModel):
    sku: str
    quantity: int = Field(..., ge=1)

class CartItemCreate(CartItemBase):
    pass

class CartItemOut(CartItemBase):
    cart_item_id: int
    added_at: datetime
    # 嵌套商品详细信息，使用 ProductOut
    product: Optional[ProductOut]

    class Config:
        orm_mode = True
