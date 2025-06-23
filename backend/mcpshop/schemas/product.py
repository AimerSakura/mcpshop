from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    name: str = Field(..., max_length=100)
    price_cents: int = Field(..., ge=0)
    stock: int = Field(..., ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    sku: str = Field(..., max_length=32)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price_cents: Optional[int] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None

class ProductOut(ProductBase):
    sku: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
