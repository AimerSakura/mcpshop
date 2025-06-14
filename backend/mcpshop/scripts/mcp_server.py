# 文件：backend/mcpshop/scripts/mcp_server.py

import os
import argparse
from dotenv import load_dotenv
from fastmcp import FastMCP
from mcpshop.crud import product as crud_product, cart as crud_cart
from mcpshop.db.session import get_db
from mcpshop.schemas.product import ProductCreate
from mcpshop.core.security import decode_access_token    # 新增
from mcpshop.crud.user import get_user_by_username       # 新增
from jose import JWTError                                 # 新增

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

@mcp.tool()
async def add_product(
    token: str,                # —— 新增：管理员 JWT
    sku: str,
    name: str,
    price_cents: int,
    stock: int,
    description: str = "",
    image_url: str = "",
    category_id: int | None = None
) -> dict:
    """
    管理员添加新商品（需携带管理员 Token）。
    """
    # —— 管理员鉴权 ——
    try:
        username = decode_access_token(token)
    except JWTError:
        raise ValueError("无效或已过期的 Token")
    async with get_db() as db:
        user = await get_user_by_username(db, username)
        if not user or not user.is_admin:
            raise ValueError("管理员权限不足")

    # 构造 Pydantic 入参
    p_in = ProductCreate(
        sku=sku,
        name=name,
        price_cents=price_cents,
        stock=stock,
        description=description,
        image_url=image_url,
        category_id=category_id
    )
    # 调用 CRUD 层创建商品
    async with get_db() as db:
        prod = await crud_product.create_product(db, p_in)
    # 返回给 LLM 简洁的字典结果
    return {
        "sku": prod.sku,
        "name": prod.name,
        "price": prod.price_cents / 100,
        "stock": prod.stock,
        "description": prod.description,
        "image_url": prod.image_url,
        "category_id": prod.category_id
    }

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
        import asyncio
        asyncio.run(mcp.serve_stdio())
    else:
        mcp.run(
            transport="streamable-http",
            host="127.0.0.1",
            port=args.port,
            path="/mcp",
            log_level="debug",
        )
