# 项目代码快照（版本 v0.1.0，2025-06-14 22:05:36）

## 项目结构

- backend
  - mcpshop
    - __init__.py
    - api
      - auth.py
      - cart.py
      - chat.py
      - deps.py
      - orders.py
      - products.py
    - core
      - __init__.py
      - config.py
      - embedding.py
      - logger.py
      - security.py
    - crud
      - __init__.py
      - cart.py
      - category.py
      - conversation.py
      - message.py
      - order.py
      - product.py
      - user.py
    - db
      - __init__.py
      - base.py
      - session.py
    - main.py
    - models
      - __init__.py
      - cart_item.py
      - category.py
      - conversation.py
      - message.py
      - order.py
      - order_item.py
      - product.py
      - user.py
    - schemas
      - __init__.py
      - auth.py
      - cart.py
      - category.py
      - chat.py
      - order.py
      - product.py
      - user.py
    - scripts
      - __init__.py
      - mcp_server.py
    - services
      - mcp_client.py

## 目录

- [backend\mcpshop\__init__.py](#backend\mcpshop\__init__py)
- [backend\mcpshop\api\auth.py](#backend\mcpshop\api\authpy)
- [backend\mcpshop\api\cart.py](#backend\mcpshop\api\cartpy)
- [backend\mcpshop\api\chat.py](#backend\mcpshop\api\chatpy)
- [backend\mcpshop\api\deps.py](#backend\mcpshop\api\depspy)
- [backend\mcpshop\api\orders.py](#backend\mcpshop\api\orderspy)
- [backend\mcpshop\api\products.py](#backend\mcpshop\api\productspy)
- [backend\mcpshop\core\__init__.py](#backend\mcpshop\core\__init__py)
- [backend\mcpshop\core\config.py](#backend\mcpshop\core\configpy)
- [backend\mcpshop\core\embedding.py](#backend\mcpshop\core\embeddingpy)
- [backend\mcpshop\core\logger.py](#backend\mcpshop\core\loggerpy)
- [backend\mcpshop\core\security.py](#backend\mcpshop\core\securitypy)
- [backend\mcpshop\crud\__init__.py](#backend\mcpshop\crud\__init__py)
- [backend\mcpshop\crud\cart.py](#backend\mcpshop\crud\cartpy)
- [backend\mcpshop\crud\category.py](#backend\mcpshop\crud\categorypy)
- [backend\mcpshop\crud\conversation.py](#backend\mcpshop\crud\conversationpy)
- [backend\mcpshop\crud\message.py](#backend\mcpshop\crud\messagepy)
- [backend\mcpshop\crud\order.py](#backend\mcpshop\crud\orderpy)
- [backend\mcpshop\crud\product.py](#backend\mcpshop\crud\productpy)
- [backend\mcpshop\crud\user.py](#backend\mcpshop\crud\userpy)
- [backend\mcpshop\db\__init__.py](#backend\mcpshop\db\__init__py)
- [backend\mcpshop\db\base.py](#backend\mcpshop\db\basepy)
- [backend\mcpshop\db\session.py](#backend\mcpshop\db\sessionpy)
- [backend\mcpshop\main.py](#backend\mcpshop\mainpy)
- [backend\mcpshop\models\__init__.py](#backend\mcpshop\models\__init__py)
- [backend\mcpshop\models\cart_item.py](#backend\mcpshop\models\cart_itempy)
- [backend\mcpshop\models\category.py](#backend\mcpshop\models\categorypy)
- [backend\mcpshop\models\conversation.py](#backend\mcpshop\models\conversationpy)
- [backend\mcpshop\models\message.py](#backend\mcpshop\models\messagepy)
- [backend\mcpshop\models\order.py](#backend\mcpshop\models\orderpy)
- [backend\mcpshop\models\order_item.py](#backend\mcpshop\models\order_itempy)
- [backend\mcpshop\models\product.py](#backend\mcpshop\models\productpy)
- [backend\mcpshop\models\user.py](#backend\mcpshop\models\userpy)
- [backend\mcpshop\schemas\__init__.py](#backend\mcpshop\schemas\__init__py)
- [backend\mcpshop\schemas\auth.py](#backend\mcpshop\schemas\authpy)
- [backend\mcpshop\schemas\cart.py](#backend\mcpshop\schemas\cartpy)
- [backend\mcpshop\schemas\category.py](#backend\mcpshop\schemas\categorypy)
- [backend\mcpshop\schemas\chat.py](#backend\mcpshop\schemas\chatpy)
- [backend\mcpshop\schemas\order.py](#backend\mcpshop\schemas\orderpy)
- [backend\mcpshop\schemas\product.py](#backend\mcpshop\schemas\productpy)
- [backend\mcpshop\schemas\user.py](#backend\mcpshop\schemas\userpy)
- [backend\mcpshop\scripts\__init__.py](#backend\mcpshop\scripts\__init__py)
- [backend\mcpshop\scripts\mcp_server.py](#backend\mcpshop\scripts\mcp_serverpy)
- [backend\mcpshop\services\mcp_client.py](#backend\mcpshop\services\mcp_clientpy)

### `backend\mcpshop\__init__.py`
- 行数：18 行  
- 大小：0.47 KB  
- 最后修改：2025-06-14 20:44:59  

```py
# mcpshop/__init__.py

"""
SmartStore 应用包初始化。

这里将常用的配置和日志器暴露到包级别，方便在项目中直接：
    from mcpshop import settings, logger
而无需每次都写完整路径。
"""
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\CodeProject\Pycharm\MCPshop\.env")
# —— 包级别导出 ——
from .core.config import settings
from .core.logger import logger

__all__ = ["settings", "logger"]

```

### `backend\mcpshop\api\auth.py`
- 行数：40 行  
- 大小：1.58 KB  
- 最后修改：2025-06-11 17:35:46  

```py
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

```

### `backend\mcpshop\api\cart.py`
- 行数：41 行  
- 大小：1.3 KB  
- 最后修改：2025-06-11 16:59:02  

```py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.db.session import get_db
from mcpshop.crud.cart import add_to_cart, remove_cart_item, get_cart_items, clear_cart
from mcpshop.schemas.cart import CartItemCreate, CartItemOut
from mcpshop.api.deps import get_current_user

router = APIRouter(prefix="/api/cart", tags=["cart"])

@router.post("/", response_model=CartItemOut)
async def add_item(
    item: CartItemCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await add_to_cart(db, user.user_id, item.sku, item.quantity)

@router.get("/", response_model=List[CartItemOut])
async def list_cart(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_cart_items(db, user.user_id)

@router.delete("/{cart_item_id}", status_code=204)
async def delete_item(
    cart_item_id: int,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 可验证归属
    await remove_cart_item(db, cart_item_id)

@router.delete("/clear", status_code=204)
async def clear_user_cart(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await clear_cart(db, user.user_id)
```

### `backend\mcpshop\api\chat.py`
- 行数：73 行  
- 大小：2.48 KB  
- 最后修改：2025-06-11 21:36:12  

```py
# mcpshop/api/chat.py
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.api.deps import get_current_user, get_db
from mcpshop.schemas.chat import ChatRequest        # ← 按你原来的位置调整
from mcpshop.services.mcp_client import MCPClient
from mcpshop.crud.cart import get_cart_items        # add_to_cart 已在 Tool 里做了，这里只读

router = APIRouter()

# ------------------------------------------------------------------
# 共用一个 MCPClient；首次使用时再启动/连接本地 MCP Server
# ------------------------------------------------------------------
_ai = MCPClient()
_SERVER_SCRIPT = str(Path(__file__).resolve().parents[2] / "scripts/mcp_server.py")


async def _ensure_ai_ready() -> None:
    if _ai.session is None:                         # 尚未连接
        await _ai.connect_to_server(_SERVER_SCRIPT)


# ------------------------------------------------------------------
# 1)  REST 端点：POST /api/chat
# ------------------------------------------------------------------
@router.post("/api/chat", summary="REST 对话接口")
async def chat_endpoint(
    req: ChatRequest,
    current=Depends(get_current_user),
):
    """
    请求体： {"text": "..."}
    返回：   {"reply": "...", "actions":[...]}
    """
    await _ensure_ai_ready()
    result = await _ai.process_query(req.text)      # 无需 user_id 时直接发文本
    return result


# ------------------------------------------------------------------
# 2)  WebSocket：/api/chat
# ------------------------------------------------------------------
@router.websocket("/api/chat")
async def websocket_chat(
    ws: WebSocket,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ws.accept()
    await _ensure_ai_ready()

    try:
        while True:
            text = await ws.receive_text()

            # 调大模型
            result = await _ai.process_query(text)

            # （可选）根据动作刷新购物车；Tool 已经写库，这里只查询展示
            cart_items = await get_cart_items(db, user.user_id)

            await ws.send_json(
                {
                    "reply": result["reply"],
                    "actions": result.get("actions", []),
                    "cart": cart_items,
                }
            )
    except WebSocketDisconnect:
        pass

```

### `backend\mcpshop\api\deps.py`
- 行数：29 行  
- 大小：0.96 KB  
- 最后修改：2025-06-11 16:59:02  

```py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.core.config import settings
from mcpshop.core.security import decode_access_token
from mcpshop.db.session import get_db
from mcpshop.crud.user import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username: str = decode_access_token(token)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_username(db, username)
    if not user:
        raise credentials_exception
    return user
```

### `backend\mcpshop\api\orders.py`
- 行数：36 行  
- 大小：1.21 KB  
- 最后修改：2025-06-11 17:30:55  

```py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.db.session import get_db
from mcpshop.crud.cart import get_cart_items, clear_cart  # ✅ 补齐缺失 import
from mcpshop.crud.order import create_order, get_orders_by_user
from mcpshop.api.deps import get_current_user
from mcpshop.schemas.order import OrderOut

router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.post("/", response_model=OrderOut)
async def place_order(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    items = await get_cart_items(db, user.user_id)
    if not items:
        raise HTTPException(status_code=400, detail="购物车为空")

    # 构造订单明细
    details = [{"sku": i.sku, "quantity": i.quantity} for i in items]
    order = await create_order(db, user.user_id, details)

    # 下单成功后清空购物车
    await clear_cart(db, user.user_id)
    return order

@router.get("/", response_model=List[OrderOut])
async def list_orders(
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_orders_by_user(db, user.user_id)

```

### `backend\mcpshop\api\products.py`
- 行数：61 行  
- 大小：1.97 KB  
- 最后修改：2025-06-11 16:59:02  

```py
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.db.session import get_db
from mcpshop.schemas.product import ProductCreate, ProductOut, ProductUpdate
from mcpshop.crud.product import (
    create_product, get_product_by_sku, search_products,
    )

router = APIRouter(prefix="/api/products", tags=["products"])

@router.post("/", response_model=ProductOut)
async def create(p: ProductCreate, db: AsyncSession = Depends(get_db)):
    exists = await get_product_by_sku(db, p.sku)
    if exists:
        raise HTTPException(status_code=400, detail="SKU 已存在")
    return await create_product(db, p)

@router.get("/", response_model=List[ProductOut])
async def list_products(
    q: str = Query("", description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await search_products(db, q, limit)

@router.get("/{sku}", response_model=ProductOut)
async def get_sku(
    sku: str, db: AsyncSession = Depends(get_db)
):
    prod = await get_product_by_sku(db, sku)
    if not prod:
        raise HTTPException(status_code=404, detail="未找到商品")
    return prod

@router.patch("/{sku}", response_model=ProductOut)
async def update_sku(
    sku: str,
    p: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    prod = await get_product_by_sku(db, sku)
    if not prod:
        raise HTTPException(status_code=404, detail="未找到商品")
    for k, v in p.dict(exclude_unset=True).items():
        setattr(prod, k, v)
    await db.commit()
    await db.refresh(prod)
    return prod

@router.delete("/{sku}", status_code=204)
async def delete_sku(
    sku: str, db: AsyncSession = Depends(get_db)
):
    prod = await get_product_by_sku(db, sku)
    if not prod:
        raise HTTPException(status_code=404, detail="未找到商品")
    await db.delete(prod)
    await db.commit()

```

### `backend\mcpshop\core\__init__.py`
- 行数：1 行  
- 大小：0.03 KB  
- 最后修改：2025-05-28 14:56:08  

```py
from .config import Settings
```

### `backend\mcpshop\core\config.py`
- 行数：37 行  
- 大小：1.13 KB  
- 最后修改：2025-06-12 00:25:42  

```py
# mcpshop/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl


class Settings(BaseSettings):
    # —— 项目基础信息 ——  
    PROJECT_NAME: str = "SmartStore"
    VERSION: str = "0.1.0"

    # —— 数据库 & 缓存 ——  
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # —— JWT ——  
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # —— MCP Server ——  
    MCP_API_URL: AnyUrl = Field(..., env="MCP_API_URL")
    MCP_API_KEY: str | None = Field(None, env="MCP_API_KEY")

    # —— OpenAI / MCPClient ——  
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    BASE_URL: str | None = Field(None, env="BASE_URL")
    MODEL: str = Field("deepseek-reasoner", env="MODEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"       # 忽略 .env 中多余未经声明的变量


# 在模块顶层实例化
settings = Settings()

```

### `backend\mcpshop\core\embedding.py`
- 行数：39 行  
- 大小：1.39 KB  
- 最后修改：2025-06-11 21:07:14  

```py
# mcpshop/core/embedding.py

import subprocess
import json
from chromadb.utils import embedding_functions

class LocalQwenEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_dir: str):
        # model_dir 指向 backend/gme-Qwen2-VL-7B-Instruct 的根目录
        self.model_dir = model_dir

    def embed(self, texts: list[str]) -> list[list[float]]:
        """
        调用本地模型脚本进行推理，假设你在 model_dir 下有一个 inference.py
        接受 JSON 输入并返回 JSON 输出。
        """
        payload = json.dumps({"texts": texts})
        # 以子进程方式调用，或换成你实际的推理接口
        proc = subprocess.Popen(
            ["python", f"{self.model_dir}/inference.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, err = proc.communicate(payload)
        if proc.returncode != 0:
            raise RuntimeError(f"嵌入模型调用失败：{err}")
        result = json.loads(out)
        return result["embeddings"]

# 在你的 AIClient 初始化中：
from mcpshop.core.embedding import LocalQwenEmbeddingFunction
from mcpshop.core.config import settings

self.embedding_fn = LocalQwenEmbeddingFunction(
    model_dir=settings.BASE_DIR / "backend" / "gme-Qwen2-VL-7B-Instruct"
)

```

### `backend\mcpshop\core\logger.py`
- 行数：23 行  
- 大小：0.63 KB  
- 最后修改：2025-05-28 15:10:24  

```py
# mcpshop/core/logger.py
from loguru import logger
import sys

# 移除默认的 logger，以便自定义配置
logger.remove()

# 添加一个 stdout 日志器，INFO 及以上级别
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{line}</cyan> - {message}"
)

# 如果需要写入文件，也可以：
# logger.add("logs/app_{time:YYYY-MM-DD}.log", rotation="00:00", level="INFO")

# 在项目任何地方直接：
# from mcpshop.core.logger import logger
# logger.info("应用启动")

```

### `backend\mcpshop\core\security.py`
- 行数：64 行  
- 大小：1.87 KB  
- 最后修改：2025-05-28 15:10:24  

```py
# mcpshop/core/security.py

from mcpshop.core.config import settings
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文与哈希密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    将明文密码哈希后返回
    """
    return pwd_context.hash(password)

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT，sub 字段为 subject（通常为 username 或 user_id）。
    过期时间可选，默认使用配置里的分钟数。
    """
    to_encode = {"sub": str(subject)}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> str:
    """
    解码 JWT，返回 sub。如果无效或过期，则抛出 JWTError。
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        subject: str = payload.get("sub")
        if subject is None:
            raise JWTError("Token payload missing 'sub'")
        return subject
    except JWTError as e:
        # 可以在这里统一抛出自定义认证异常
        raise

```

### `backend\mcpshop\crud\__init__.py`
- 行数：8 行  
- 大小：0.16 KB  
- 最后修改：2025-06-11 13:19:43  

```py
from .user import *
from .category import *
from .product import *
from .cart import *
from .order import *
from .conversation import *
from .message import *

```

### `backend\mcpshop\crud\cart.py`
- 行数：46 行  
- 大小：1.67 KB  
- 最后修改：2025-06-11 17:33:48  

```py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from mcpshop.models.cart_item import CartItem
from mcpshop.models.product import Product                 # ✅ 用于库存校验
from mcpshop.schemas.cart import CartItemCreate

async def add_to_cart(db: AsyncSession, user_id: int, sku: str, quantity: int = 1) -> CartItem:
    # ✅ 校验商品存在 & 库存充足
    prod = await db.get(Product, sku)
    if not prod or prod.stock < quantity:
        raise ValueError("商品不存在或库存不足")

    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.sku == sku)
    )
    item = result.scalars().first()
    if item:
        if prod.stock < item.quantity + quantity:
            raise ValueError("库存不足")
        item.quantity += quantity
    else:
        item = CartItem(user_id=user_id, sku=sku, quantity=quantity)
        db.add(item)

    await db.commit()
    await db.refresh(item)
    return item


async def remove_cart_item(db: AsyncSession, cart_item_id: int) -> None:
    stmt = select(CartItem).where(CartItem.cart_item_id == cart_item_id)
    result = await db.execute(stmt)
    item = result.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()

async def get_cart_items(db: AsyncSession, user_id: int) -> list[CartItem]:
    result = await db.execute(select(CartItem).where(CartItem.user_id == user_id))
    return result.scalars().all()

async def clear_cart(db: AsyncSession, user_id: int) -> None:
    items = await get_cart_items(db, user_id)
    for item in items:
        await db.delete(item)
    await db.commit()
```

### `backend\mcpshop\crud\category.py`
- 行数：19 行  
- 大小：0.73 KB  
- 最后修改：2025-06-11 13:20:47  

```py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mcpshop.models.category import Category
from mcpshop.schemas.category import CategoryCreate

async def create_category(db: AsyncSession, cat_in: CategoryCreate) -> Category:
    cat = Category(name=cat_in.name)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat

async def get_category(db: AsyncSession, category_id: int) -> Category | None:
    result = await db.execute(select(Category).where(Category.category_id == category_id))
    return result.scalars().first()

async def list_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category))
    return result.scalars().all()
```

### `backend\mcpshop\crud\conversation.py`
- 行数：15 行  
- 大小：0.59 KB  
- 最后修改：2025-06-11 13:22:25  

```py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mcpshop.models.conversation import Conversation

async def create_conversation(db: AsyncSession, user_id: int, session_id: str) -> Conversation:
    conv = Conversation(user_id=user_id, session_id=session_id)
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv

async def get_conversation(db: AsyncSession, conv_id: int) -> Conversation | None:
    result = await db.execute(select(Conversation).where(Conversation.conv_id == conv_id))
    return result.scalars().first()

```

### `backend\mcpshop\crud\message.py`
- 行数：16 行  
- 大小：0.68 KB  
- 最后修改：2025-06-11 17:32:25  

```py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from mcpshop.models.message import Message, Sender          # ✅ 引入枚举
from mcpshop.schemas.chat import MessageIn

async def add_message(db: AsyncSession, conv_id: int, sender: str, content: str) -> Message:
    msg = Message(conv_id=conv_id, sender=Sender(sender), content=content)  # ✅ 枚举化
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg

async def get_messages(db: AsyncSession, conv_id: int) -> list[Message]:
    result = await db.execute(select(Message).where(Message.conv_id == conv_id).order_by(Message.created_at))
    return result.scalars().all()

```

### `backend\mcpshop\crud\order.py`
- 行数：42 行  
- 大小：1.52 KB  
- 最后修改：2025-06-11 17:32:03  

```py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from mcpshop.models.order import Order
from mcpshop.models.order_item import OrderItem
from mcpshop.models.product import Product

async def create_order(db: AsyncSession, user_id: int, items: list[dict]) -> Order:
    total = 0
    order = Order(user_id=user_id, total_cents=0)
    db.add(order)
    await db.flush()                      # 先拿到 order_id

    for it in items:
        prod: Product = await db.get(Product, it["sku"], with_for_update=True)  # ✅ 行锁保证并发安全
        if not prod:
            raise ValueError(f"商品 {it['sku']} 不存在")
        qty = it["quantity"]
        if prod.stock < qty:
            raise ValueError(f"商品 {prod.sku} 库存不足")
        total += prod.price_cents * qty
        db.add(OrderItem(
            order_id=order.order_id,
            sku=prod.sku,
            quantity=qty,
            unit_price=prod.price_cents
        ))
        prod.stock -= qty

    order.total_cents = total
    await db.commit()
    await db.refresh(order, ["items"])     # ✅ 提前加载 items，避免懒加载失败
    return order

async def get_orders_by_user(db: AsyncSession, user_id: int) -> List[Order]:
    result = await db.execute(
        select(Order).options(selectinload(Order.items))   # ✅ 解决 MissingGreenlet
        .where(Order.user_id == user_id)
    )
    return result.scalars().all()

```

### `backend\mcpshop\crud\product.py`
- 行数：37 行  
- 大小：1.28 KB  
- 最后修改：2025-06-11 20:38:52  

```py
# app/crud/product.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from typing import List
from mcpshop.models.product import Product
from mcpshop.schemas.product import ProductCreate

async def get_all_products(db: AsyncSession) -> List[Product]:
    result = await db.execute(select(Product))
    return result.scalars().all()

async def create_product(db: AsyncSession, p_in: ProductCreate) -> Product:
    prod = Product(
        sku=p_in.sku,
        name=p_in.name,
        price_cents=p_in.price_cents,
        stock=p_in.stock,
        description=p_in.description,
        image_url=p_in.image_url,
        category_id=p_in.category_id
    )
    db.add(prod)
    await db.commit()
    await db.refresh(prod)
    return prod

async def get_product_by_sku(db: AsyncSession, sku: str) -> Product | None:
    result = await db.execute(select(Product).where(Product.sku == sku))
    return result.scalars().first()

async def search_products(db: AsyncSession, q: str, limit: int = 20) -> List[Product]:
    stmt = select(Product).where(
        or_(Product.name.ilike(f"%{q}%"), Product.description.ilike(f"%{q}%"))
    ).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### `backend\mcpshop\crud\user.py`
- 行数：27 行  
- 大小：1.0 KB  
- 最后修改：2025-06-11 13:20:15  

```py
# app/crud/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mcpshop.models.user import User
from mcpshop.core.security import get_password_hash, verify_password
from mcpshop.schemas.user import UserCreate

async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

### `backend\mcpshop\db\__init__.py`
- 行数：1 行  
- 大小：0.0 KB  
- 最后修改：2025-05-28 14:58:20  

```py

```

### `backend\mcpshop\db\base.py`
- 行数：14 行  
- 大小：0.44 KB  
- 最后修改：2025-05-28 15:10:24  

```py
# mcpshop/db/base.py

from sqlalchemy.orm import declarative_base

# 1. 创建所有 ORM model 的基类
Base = declarative_base()

# 2. （可选）在这里 import 所有 model，确保它们被注册到 Base.metadata
#    这样在运行 Alembic autogenerate 时才能发现所有表
# from mcpshop.models.user import User
# from mcpshop.models.product import Product
# from mcpshop.models.cart_item import CartItem
# ... 依此类推

```

### `backend\mcpshop\db\session.py`
- 行数：34 行  
- 大小：1.15 KB  
- 最后修改：2025-06-14 21:21:41  

```py
# mcpshop/db/session.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from mcpshop.core.config import settings
from contextlib import asynccontextmanager
# 1. 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,  # 格式示例：mysql+asyncmy://user:pass@host:3306/dbname
    echo=True,  # 是否打印 SQL 到控制台，开发时可开，生产可关
    future=True  # 使用 2.0 风格 API
)

# 2. 创建 sessionmaker，用于产生 AsyncSession
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # 提交后不 expire 对象，便于后续访问属性
)


# 3. 依赖注入函数：在 FastAPI 路由中使用 Depends(get_db)
@asynccontextmanager
async def get_db() -> AsyncSession:
    """
    Yield 一个 AsyncSession，并在使用完后自动关闭连接。
    用法示例：
        @router.get("/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(...)
    """
    async with AsyncSessionLocal() as session:
        yield session

```

### `backend\mcpshop\main.py`
- 行数：54 行  
- 大小：1.63 KB  
- 最后修改：2025-06-14 20:29:07  

```py
# mcpshop/main.py
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\CodeProject\Pycharm\MCPshop\.env")

# # 验证环境变量是否正确加载
# print("DATABASE_URL:", os.getenv("DATABASE_URL"))
# print("REDIS_URL:", os.getenv("REDIS_URL"))
# print("JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))
# print("MCP_API_URL:", os.getenv("MCP_API_URL"))
# print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcpshop.core.config import settings
from mcpshop.api import auth, cart, chat, orders, products
from mcpshop.db.session import engine
from mcpshop.db.base import Base
import uvicorn

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION
    )
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 路由
    app.include_router(auth.router)
    app.include_router(cart.router)
    app.include_router(chat.router)
    app.include_router(orders.router)
    app.include_router(products.router)

    @app.on_event("startup")
    async def on_startup() -> None:
        # **开发演示**：直接创建表。生产请换成 Alembic 迁移。
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("mcpshop.main:app", host="127.0.0.1", port=8000, reload=True)

```

### `backend\mcpshop\models\__init__.py`
- 行数：8 行  
- 大小：0.24 KB  
- 最后修改：2025-05-28 14:51:14  

```py
from .user import User
from .product import Product
from .category import Category
from .cart_item import CartItem
from .order import Order
from .order_item import OrderItem
from .conversation import Conversation
from .message import Message
```

### `backend\mcpshop\models\cart_item.py`
- 行数：16 行  
- 大小：0.73 KB  
- 最后修改：2025-05-28 15:10:24  

```py
from sqlalchemy import Column, BigInteger, Integer, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base

class CartItem(Base):
    __tablename__ = "cart_items"
    cart_item_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    sku = Column(String(32), ForeignKey("products.sku"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

```

### `backend\mcpshop\models\category.py`
- 行数：10 行  
- 大小：0.37 KB  
- 最后修改：2025-06-11 13:17:19  

```py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")
```

### `backend\mcpshop\models\conversation.py`
- 行数：15 行  
- 大小：0.68 KB  
- 最后修改：2025-06-11 13:17:19  

```py
from sqlalchemy import Column, BigInteger, DateTime, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base

class Conversation(Base):
    __tablename__ = "conversations"
    conv_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    session_id = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

```

### `backend\mcpshop\models\message.py`
- 行数：20 行  
- 大小：0.73 KB  
- 最后修改：2025-06-11 13:17:19  

```py
from sqlalchemy import Column, BigInteger, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base
import enum

class Sender(enum.Enum):
    USER = "user"
    BOT = "bot"

class Message(Base):
    __tablename__ = "messages"
    message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    conv_id = Column(BigInteger, ForeignKey("conversations.conv_id"), nullable=False)
    sender = Column(SQLEnum(Sender), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

```

### `backend\mcpshop\models\order.py`
- 行数：23 行  
- 大小：0.89 KB  
- 最后修改：2025-06-11 13:17:19  

```py
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base
import enum

class OrderStatus(enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    SHIPPED = "SHIPPED"

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    total_cents = Column(BigInteger, nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

```

### `backend\mcpshop\models\order_item.py`
- 行数：14 行  
- 大小：0.65 KB  
- 最后修改：2025-06-11 13:17:19  

```py
from sqlalchemy import Column, BigInteger, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.order_id"), nullable=False)
    sku = Column(String(32), ForeignKey("products.sku"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
```

### `backend\mcpshop\models\product.py`
- 行数：21 行  
- 大小：0.99 KB  
- 最后修改：2025-06-11 13:17:19  

```py
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base

class Product(Base):
    __tablename__ = "products"
    sku = Column(String(32), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    price_cents = Column(Integer, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

```

### `backend\mcpshop\models\user.py`
- 行数：17 行  
- 大小：0.91 KB  
- 最后修改：2025-06-11 13:17:19  

```py
from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
```

### `backend\mcpshop\schemas\__init__.py`
- 行数：11 行  
- 大小：0.42 KB  
- 最后修改：2025-05-28 15:19:29  

```py
# app/schemas/__init__.py

# 统一导出，方便在路由里一次性 import
from .user import UserCreate, UserOut
from .auth import Token, TokenData
from .category import CategoryCreate, CategoryOut
from .product import ProductCreate, ProductOut, ProductUpdate
from .cart import CartItemCreate, CartItemOut
from .order import OrderCreate, OrderOut, OrderItemOut
from .chat import MessageIn, MessageOut, ConversationOut

```

### `backend\mcpshop\schemas\auth.py`
- 行数：10 行  
- 大小：0.19 KB  
- 最后修改：2025-05-28 15:20:24  

```py
# app/schemas/auth.py
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: str | None = None

```

### `backend\mcpshop\schemas\cart.py`
- 行数：21 行  
- 大小：0.44 KB  
- 最后修改：2025-05-28 15:21:27  

```py
# app/schemas/cart.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CartItemBase(BaseModel):
    sku: str
    quantity: int = Field(..., ge=1)

class CartItemCreate(CartItemBase):
    ...

class CartItemOut(CartItemBase):
    cart_item_id: int
    added_at: datetime
    # 嵌套商品简略信息
    product: Optional[dict]

    class Config:
        orm_mode = True

```

### `backend\mcpshop\schemas\category.py`
- 行数：15 行  
- 大小：0.29 KB  
- 最后修改：2025-05-28 15:20:45  

```py
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

```

### `backend\mcpshop\schemas\chat.py`
- 行数：27 行  
- 大小：0.53 KB  
- 最后修改：2025-06-11 21:37:36  

```py
# app/schemas/chat.py
from pydantic import BaseModel
from datetime import datetime
from typing import Literal, List

class MessageIn(BaseModel):
    content: str

class MessageOut(BaseModel):
    message_id: int
    sender: Literal['user','bot']
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

class ConversationOut(BaseModel):
    conv_id: int
    session_id: str
    messages: List[MessageOut]

    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    text: str
```

### `backend\mcpshop\schemas\order.py`
- 行数：27 行  
- 大小：0.53 KB  
- 最后修改：2025-05-28 15:21:43  

```py
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

```

### `backend\mcpshop\schemas\product.py`
- 行数：32 行  
- 大小：0.81 KB  
- 最后修改：2025-05-28 15:21:06  

```py
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

```

### `backend\mcpshop\schemas\user.py`
- 行数：19 行  
- 大小：0.43 KB  
- 最后修改：2025-05-28 15:19:53  

```py
# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserOut(UserBase):
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

```

### `backend\mcpshop\scripts\__init__.py`
- 行数：1 行  
- 大小：0.0 KB  
- 最后修改：2025-06-11 23:54:35  

```py

```

### `backend\mcpshop\scripts\mcp_server.py`
- 行数：67 行  
- 大小：2.27 KB  
- 最后修改：2025-06-14 21:09:28  

```py
# scripts/mcp_server.py

import os
import argparse
from dotenv import load_dotenv
from fastmcp import FastMCP
from mcpshop.crud import product as crud_product, cart as crud_cart
from mcpshop.db.session import get_db

# 1. 加载环境变量
load_dotenv(dotenv_path=r"C:\CodeProject\Pycharm\MCPshop\.env")

# 2. 创建 FastMCP 实例
mcp = FastMCP("SmartStoreToolServer")

# 3. 注册工具 (Tool)
@mcp.tool()
async def list_products(q: str = "", top_k: int = 5) -> list[dict]:
    """搜索商品（模糊匹配名称/描述）"""
    async with get_db() as db:
        items = await crud_product.search_products(db, q, top_k)
    return [
        {"sku": p.sku, "name": p.name, "price": p.price_cents / 100, "stock": p.stock}
        for p in items
    ]

@mcp.tool()
async def add_to_cart(user_id: int, sku: str, qty: int = 1) -> dict:
    """把指定 SKU 加入用户购物车"""
    async with get_db() as db:
        await crud_cart.add_to_cart(db, user_id, sku, qty)
    return {"ok": True}

# 4. 注册 Resource（可选）
@mcp.resource("mcpshop://products_all")
async def products_all() -> list[dict]:
    """全量商品列表资源"""
    async with get_db() as db:
        items = await crud_product.list_all_products(db)
    return [
        {"sku": p.sku, "name": p.name, "price": p.price_cents / 100}
        for p in items
    ]

# 5. 启动入口
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdio", action="store_true",
                        help="启动 STDIO 嵌入式 模式")
    parser.add_argument("--port", type=int, default=4200,
                        help="HTTP 服务端口，默认 4200")
    args = parser.parse_args()

    if args.stdio:
        # 嵌入式 STDIO 模式：供 stdio_client 使用
        import asyncio
        asyncio.run(mcp.serve_stdio())
    else:
        # HTTP 模式：Streamable HTTP + SSE
        mcp.run(
            transport="streamable-http",
            host="127.0.0.1",        # 或 "0.0.0.0" 开放到局域网
            port=args.port,          # 默认 4200，也可通过 --port 指定
            path="/mcp",             # 挂载前缀，接口在 /mcp/xxx 下
            log_level="debug",       # 输出详细日志
        )

```

### `backend\mcpshop\services\mcp_client.py`
- 行数：129 行  
- 大小：4.17 KB  
- 最后修改：2025-06-14 21:26:50  

```py
import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from fastmcp import Client
from openai import OpenAI

# 1. 载入 .env
load_dotenv(r"C:\CodeProject\Pycharm\MCPshop\.env")


class MCPClient:
    """基于 HTTP 的 MCP demo 客户端"""

    def __init__(self, server_url: str):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ 请在 .env 中设置 OPENAI_API_KEY")

        # OpenAI 同步 SDK（包装到线程池里）
        self.oa = OpenAI(api_key=api_key, base_url=os.getenv("BASE_URL") or None)
        self.model = os.getenv("MODEL", "deepseek-chat")

        # fastmcp HTTP 客户端
        self.client = Client(server_url)

    # ------------------------- 核心逻辑 -------------------------

    async def process_query(self, query: str) -> str:
        """向 LLM 发送消息，必要时自动调用 MCP 工具"""
        messages = [{"role": "user", "content": query}]

        # ① 向服务器拉取全部工具 schema
        tools = await self.client.list_tools()
        func_schemas = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": getattr(tool, "inputSchema", getattr(tool, "input_schema", {})),
                },
            }
            for tool in tools
        ]

        # ② 首轮推理（可能触发 tool_calls）
        first = await asyncio.to_thread(
            self.oa.chat.completions.create,
            model=self.model,
            messages=messages,
            tools=func_schemas,
        )
        choice = first.choices[0]

        # 无 tool_call：直接返回文本
        if choice.finish_reason != "tool_calls":
            return choice.message.content

        # ③ 执行一次工具
        tc = choice.message.tool_calls[0]
        tool_name = tc.function.name
        tool_args = json.loads(tc.function.arguments)
        print(f"[调用工具] {tool_name} {tool_args}")

        exec_res = await self.client.call_tool(tool_name, tool_args)

        # fastmcp ≥0.4 直接返回原始结果；旧版返回带 .content 的对象
        result_content = getattr(exec_res, "content", exec_res)

        # ④ 把工具结果写回对话，再次推理
        messages.append(choice.message.model_dump())
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tool_name,
                # OpenAI 要求 string，所以先转 JSON 字符串
                "content": json.dumps(result_content, ensure_ascii=False),
            }
        )

        second = await asyncio.to_thread(
            self.oa.chat.completions.create,
            model=self.model,
            messages=messages,
        )
        return second.choices[0].message.content

    # ------------------------- CLI 对话循环 -------------------------

    async def chat_loop(self):
        print("🤖 进入对话（HTTP 模式），输入 quit 退出")
        while True:
            prompt = input("你: ").strip()
            if prompt.lower() == "quit":
                break
            try:
                resp = await self.process_query(prompt)
                print("🤖:", resp)
            except Exception as e:
                print("⚠️ 出错:", e)

    async def run(self):
        async with self.client as client:
            try:
                await client.ping()
                print("✅ MCP Server 握手成功，开始对话")
            except Exception as e:
                print("❌ 握手失败，请检查 URL 或服务状态：", e)
                return
            await self.chat_loop()


# ------------------------- 入口 -------------------------

async def _main():
    if len(sys.argv) != 2:
        print("用法: python -m mcpshop.services.mcp_client <http://host:port/mcp>")
        sys.exit(1)
    url = sys.argv[1]
    client = MCPClient(url)
    await client.run()


if __name__ == "__main__":
    asyncio.run(_main())

```

