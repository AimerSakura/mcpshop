from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.db.session import get_db
from mcpshop.crud.user import get_user_by_username
from mcpshop.api.deps import get_current_admin_user
from mcpshop.schemas.user import UserOut  # ★ 用Pydantic模型 UserOut

router = APIRouter(prefix="/api/users", tags=["users"])

# 管理员获取所有用户列表
@router.get("/", response_model=List[UserOut], dependencies=[Depends(get_current_admin_user)])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute("SELECT * FROM users")
    return result.scalars().all()

# 管理员删除指定用户
@router.delete("/{username}", status_code=204, dependencies=[Depends(get_current_admin_user)])
async def delete_user(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    await db.delete(user)
    await db.commit()
