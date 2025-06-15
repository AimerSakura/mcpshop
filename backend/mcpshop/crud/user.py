# app/crud/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mcpshop.models.user import User
from mcpshop.core.security import get_password_hash, verify_password
from mcpshop.schemas.user import UserCreate
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password)
    )
    db.add(db_user)
    try:
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        await db.rollback()
        # 判断是否邮箱重复
        if "ix_users_email" in str(e):
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        if "ix_users_username" in str(e):
            raise HTTPException(status_code=400, detail="用户名已存在")
        raise