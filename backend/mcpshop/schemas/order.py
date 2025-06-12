# app/schemas/order.py
from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItemOut(BaseModel):
    sku: str
    quantity: int
    unit_price: int

    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    # 如果前端传当前购物车，就不用再传 items
    pass

class OrderOut(BaseModel):
    order_id: int
    total_cents: int
    status: str
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        orm_mode = True
