# 文件：backend/mcpshop/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
USERNAME_RE = re.compile(r"^[A-Za-z0-9]+$")

class UserBase(BaseModel):
    username: str  = Field(..., min_length=3, max_length=50)
    email:    EmailStr

class UserCreate(UserBase):
    password: str  = Field(..., min_length=6)

    # ✅ 只允许英文字母和数字
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not USERNAME_RE.fullmatch(v):
            raise ValueError("用户名只能包含英文字母和数字，且长度 3~50")
        return v

class UserOut(UserBase):
    user_id:    int
    is_admin:   bool              # —— 新增字段 ——
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True     # V2 中替代 orm_mode；原来写法见 :contentReference[oaicite:1]{index=1}
