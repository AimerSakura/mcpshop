# app/schemas/product.py
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    name: str = Field(..., max_length=100)
    price_cents: int = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    description: Optional[str]
    image_url: Optional[HttpUrl]
    category_id: Optional[int]

class ProductCreate(ProductBase):
    sku: str = Field(..., max_length=32)

class ProductUpdate(BaseModel):
    name: Optional[str]
    price_cents: Optional[int]
    stock: Optional[int]
    description: Optional[str]
    image_url: Optional[HttpUrl]
    category_id: Optional[int]

class ProductOut(ProductBase):
    sku: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
