# 文件：backend/mcpshop/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.core.security import decode_access_token
from mcpshop.db.session        import get_db
from mcpshop.crud.user         import get_user_by_username
from mcpshop.models.user       import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db:    AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username = decode_access_token(token)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(db, username)
    if not user:
        raise credentials_exception
    return user

async def get_current_admin_user(
    current: User = Depends(get_current_user),
) -> User:
    """
    仅允许 is_admin=True 的用户继续，其他返回 403。
    """
    if not current.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员权限不足"
        )
    return current
