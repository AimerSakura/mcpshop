from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from mcpshop.db.session import get_db
from mcpshop.crud.user import authenticate_user, create_user, get_user_by_username
from mcpshop.core.security import create_access_token
from mcpshop.schemas.auth import Token
from mcpshop.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # ✅ 直接检查用户名 / 邮箱重复，不再调用 authenticate_user
    if await get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    # 如有邮箱唯一约束，也可并行检查:
    # if await get_user_by_email(db, user_in.email): ...

    return await create_user(db, user_in)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.username)
    return {"access_token": access_token, "token_type": "bearer"}
