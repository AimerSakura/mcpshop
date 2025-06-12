## 项目结构

项目根目录： `C:\CodeProject\Pycharm\MCPshop`

后端模块路径： `C:\CodeProject\Pycharm\MCPshop\backend\mcpshop`

子模块：

```
mcpshop/
├── api       # 接口层
├── core      # 核心模块
├── crud      # 数据增删改查逻辑
├── db        # 数据库连接与初始化
├── models    # ORM 模型定义
├── schemas   # Pydantic 数据验证与序列化
└── services  # 业务逻辑层
```

请继续发送各模块的代码文件，我会将它们逐步添加到文档中。

------

## api 模块

目录： `mcpshop/api`

### auth.py

```python
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

### cart.py

```python
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

### chat.py

```python
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

### deps.py

```python
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

### orders.py

```python
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

### products.py

```python
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

请继续发送下一个模块的代码文件，我会继续添加。

------

## crud 模块

目录： `mcpshop/crud`

### **init**.py

```python
from .user import *
from .category import *
from .product import *
from .cart import *
from .order import *
from .conversation import *
from .message import *
```

### cart.py

```python
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

### category.py

```python
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

### conversation.py

```python
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

### message.py

```python
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

### order.py

```python
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

### product.py

```python
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

### user.py

```python
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

请继续发送下一个模块的代码文件，我会继续添加。

------

## core 模块

目录： `mcpshop/core`

### **init**.py

```python
from .config import Settings
```

### config.py

```python
# mcpshop/core/config.py
from pydantic_settings import BaseSettings        # ✅ 新位置
from pydantic import Field, AnyUrl
class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartStore"
    VERSION: str = "0.1.0"

    DATABASE_URL: AnyUrl = Field(..., env="DATABASE_URL")
    REDIS_URL: AnyUrl = Field(..., env="REDIS_URL")

    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    MCP_API_URL: AnyUrl = Field(..., env="MCP_API_URL")
    MCP_API_KEY: str = Field(..., env="MCP_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

```
### embedding.py

```python
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


### logger.py

```python
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

### security.py

```python
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

请继续发送下一个模块的代码文件，我会继续添加。

------

## db 模块

目录： `mcpshop/db`

### **init**.py

```python
# 空文件，用于标识包
```

### base.py

```python
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

### session.py

```python
# mcpshop/db/session.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from mcpshop.core.config import settings

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

请继续发送下一个模块的代码文件，我会继续添加。

------

## models 模块

目录： `mcpshop/models`

### **init**.py

```python
from .user import User
from .product import Product
from .category import Category
from .cart_item import CartItem
from .order import Order
from .order_item import OrderItem
from .conversation import Conversation
from .message import Message
```

### cart_item.py

```python
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

### category.py

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from mcpshop.db.base import Base

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")
```

### conversation.py

```python
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

### message.py

```python
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

### order.py

```python
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

### order_item.py

```python
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

### product.py

```python
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

### user.py

```python
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

请继续发送下一个模块或服务层的代码文件，我会继续添加。

------

## schemas 模块

目录： `mcpshop/schemas`

### **init**.py

```python
# 统一导出，方便在路由里一次性 import
from .user import UserCreate, UserOut
from .auth import Token, TokenData
from .category import CategoryCreate, CategoryOut
from .product import ProductCreate, ProductOut, ProductUpdate
from .cart import CartItemCreate, CartItemOut
from .order import OrderCreate, OrderOut, OrderItemOut
from .chat import MessageIn, MessageOut, ConversationOut
```

### auth.py

```python
# app/schemas/auth.py
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: str | None = None

```

### cart.py

```python
# app/schemas/cart.py
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

### category.py

```python
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

### chat.py

```python
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

### order.py

```python
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

### product.py

```python
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

### user.py

```python
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

请继续发送 services 模块或其他代码文件，我会继续添加。

------

## services 模块

目录： `mcpshop/services`

### mcp_client.py

```python
# mcpshop/services/mcp_client.py
"""
MCPClient  ——  智慧商城客户端 (Stdio + Function-Calling)
-------------------------------------------------------
✦ 环境变量 (建议放 .env)               说明
  ───────────────────────────────────────────────────────
  OPENAI_API_KEY   OpenAI API Key（必填）
  BASE_URL         OpenAI 代理 / 反向代理地址（可选）
  MODEL            默认模型，如 gpt-4o-mini（可选，默认 gpt-4o-mini）
"""

import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from typing import Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI           # 同步 SDK，用 asyncio.to_thread 包装

# ────────────────────────────────
# 环境加载
# ────────────────────────────────
load_dotenv()                       # 读取 .env


class MCPClient:
    """对话客户端：负责
    1. 启动 / 连接 MCP Server (Stdio)
    2. 把可用工具列表交给 OpenAI 进行 Function-Calling
    3. 若触发 tool_calls，则执行并把结果回传给模型
    """

    def __init__(self) -> None:
        self.exit_stack = AsyncExitStack()

        # ── OpenAI 配置 ────────────────────────────────────────────
        self.openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("❌ 未找到 OPENAI_API_KEY，请在 .env 中设置")

        self.base_url: str | None = os.getenv("BASE_URL")  # 代理 / 反代
        self.model: str = os.getenv("MODEL", "gpt-4o-mini")

        # 同步客户端；后续用 asyncio.to_thread 调用避免阻塞事件循环
        self.oa = OpenAI(api_key=self.openai_api_key, base_url=self.base_url)

        # MCP 连接对象
        self.session: Optional[ClientSession] = None
        self.stdio = None            # read_stream
        self.write = None            # write_stream (send)

    # ──────────────────────────────────────────────────────────────
    # 1) 连接 / 启动服务器
    # ──────────────────────────────────────────────────────────────
    async def connect_to_server(self, server_script_path: str) -> None:
        """
        启动（或连接）MCP 服务器脚本（.py / .js 均可）
        """
        ext = os.path.splitext(server_script_path)[1]
        if ext not in {".py", ".js"}:
            raise ValueError("服务器脚本必须是 .py 或 .js 文件!")

        command = "python" if ext == ".py" else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None,                # 继承默认环境变量
        )

        # 启动子进程并建立 stdin/stdout 双流
        self.stdio, self.write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        # 创建 Session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.session.initialize()       # 握手

        # 列出工具
        tools_resp = await self.session.list_tools()
        tool_names = [t.name for t in tools_resp.tools]
        print("✅ 已连接 MCP 服务器，支持工具:", tool_names)

    # ──────────────────────────────────────────────────────────────
    # 2) 处理单轮查询
    # ──────────────────────────────────────────────────────────────
    async def process_query(self, query: str) -> str:
        """
        发给 OpenAI → 解析 tool_calls → 执行工具 → 二次回复
        """
        if self.session is None:
            raise RuntimeError("❌ 未连接到服务器，请先调用 connect_to_server()")

        # 基础对话历史（可扩展为存储上下文）
        messages = [{"role": "user", "content": query}]

        # ── ① 获取工具 schema 列表
        list_resp = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema,  # OpenAI 1.x 需用 parameters/key
                },
            }
            for t in list_resp.tools
        ]

        # ── ② 第一次调用大模型（可能触发工具）
        first_resp = await asyncio.to_thread(
            self.oa.chat.completions.create,
            model=self.model,
            messages=messages,
            tools=available_tools,
        )
        choice = first_resp.choices[0]

        # 未触发工具
        if choice.finish_reason != "tool_calls":
            return choice.message.content

        # ── ③ 若有 tool_calls，执行并回写
        tool_call = choice.message.tool_calls[0]          # 演示只取第一个
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        # 执行工具
        print(f"\n[Tool] → {tool_name} {tool_args}")
        exec_result = await self.session.call_tool(tool_name, tool_args)

        # 把执行结果加入对话
        messages.append(choice.message.model_dump())
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,             # 必需
                "name": tool_name,
                "content": json.dumps(exec_result.content),
            }
        )

        # ── ④ 第二次让模型生成最终回复
        second_resp = await asyncio.to_thread(
            self.oa.chat.completions.create,
            model=self.model,
            messages=messages,
        )
        return second_resp.choices[0].message.content

    # ──────────────────────────────────────────────────────────────
    # 3) 命令行对话循环 (Demo)
    # ──────────────────────────────────────────────────────────────
    async def chat_loop(self) -> None:
        """简单 CLI，输入 quit 退出"""
        print("\n🤖 进入对话，输入 quit 退出。")
        while True:
            try:
                user_in = input("\n你: ").strip()
                if user_in.lower() == "quit":
                    break
                reply = await self.process_query(user_in)
                print(f"\n🤖: {reply}")
            except Exception as exc:
                print(f"\n⚠️ 发生错误: {exc}")

    # ──────────────────────────────────────────────────────────────
    # 4) 资源清理
    # ──────────────────────────────────────────────────────────────
    async def cleanup(self) -> None:
        """退出时关闭所有 async context"""
        await self.exit_stack.aclose()


# ──────────────────────────────────────────────────────────────────
# CLI 入口：python -m mcpshop.services.mcp_client <path_to_server.py>
# ──────────────────────────────────────────────────────────────────
async def _main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m mcpshop.services.mcp_client scripts/mcp_server.py")
        sys.exit(1)

    server_path = sys.argv[1]
    client = MCPClient()

    try:
        await client.connect_to_server(server_path)
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(_main())

```

## scripts 模块


目录： `mcpshop/scripts`

### mcp_server.py
```python
# scripts/mcp_server.py
"""
Smart-Store MCP Server  (FastMCP 版本)
-------------------------------------
✦ 对外暴露三项能力
   1. list_products        → 商品检索
   2. add_to_cart          → 加入购物车
   3. products_all (Resource) → 全量商品资源

✦ 支持两种启动方式
   • ASGI (默认)：      python scripts/mcp_server.py
   • stdio（嵌入式）：  python scripts/mcp_server.py --stdio
"""

from typing import List
import asyncio
import argparse

from mcp.server.fastmcp import FastMCP
from mcpshop.crud import product as crud_product, cart as crud_cart
from mcpshop.db.session import get_db

mcp = FastMCP("SmartStoreToolServer")

# ---------- Tools -------------------------------------------------
@mcp.tool()
async def list_products(q: str = "", top_k: int = 5) -> List[dict]:
    """搜索商品（模糊匹配名称/描述）"""
    async with get_db() as db:
        items = await crud_product.search_products(db, q, top_k)
    return [
        {
            "sku": p.sku,
            "name": p.name,
            "price": p.price_cents / 100,
            "stock": p.stock,
        }
        for p in items
    ]


@mcp.tool()
async def add_to_cart(user_id: int, sku: str, qty: int = 1) -> dict:
    """把指定 SKU 加入用户购物车"""
    async with get_db() as db:
        await crud_cart.add_to_cart(db, user_id, sku, qty)
    return {"ok": True}


# ---------- Resource ----------------------------------------------
@mcp.resource("products_all")
async def products_all() -> List[dict]:
    """暴露全量商品信息作为 Resource"""
    async with get_db() as db:
        items = await crud_product.list_all_products(db)
    return [
        {"sku": p.sku, "name": p.name, "price": p.price_cents / 100}
        for p in items
    ]


# ---------- Run ----------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdio", action="store_true", help="Serve via stdio")
    parser.add_argument("--port", type=int, default=8001, help="HTTP port")
    args = parser.parse_args()

    if args.stdio:
        # 嵌入到其他进程（如 MCPClient）时使用
        asyncio.run(mcp.serve_stdio())
    else:
        import uvicorn

        # 独立进程运行，暴露 HTTP / WebSocket 接口
        uvicorn.run(mcp.app, host="0.0.0.0", port=args.port)

```