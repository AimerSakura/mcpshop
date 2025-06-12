# app/schemas/category.py
from pydantic import BaseModel, Field

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=50)

class CategoryCreate(CategoryBase):
    ...

class CategoryOut(CategoryBase):
    category_id: int

    class Config:
        orm_mode = True
