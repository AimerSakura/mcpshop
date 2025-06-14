# 文件：backend/mcpshop/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
class UserBase(BaseModel):
    username: str    = Field(..., min_length=3, max_length=50)
    email:    EmailStr

class UserCreate(UserBase):
    password: str    = Field(..., min_length=6)

class UserOut(UserBase):
    user_id:    int
    is_admin:   bool              # —— 新增字段 ——
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True     # V2 中替代 orm_mode；原来写法见 :contentReference[oaicite:1]{index=1}
