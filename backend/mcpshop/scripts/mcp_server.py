import os
import argparse
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from mcpshop.db.session import AsyncSessionLocal
from mcpshop.crud import product as crud_product, cart as crud_cart
from mcpshop.schemas.product import ProductCreate
from mcpshop.core.security import decode_access_token
from mcpshop.crud.user import get_user_by_username
from sqlalchemy.exc import IntegrityError
from jose import JWTError

# 强制覆盖系统环境变量
load_dotenv(r"C:\CodeProject\Pycharm\MCPshop\.env", override=True)

mcp = FastMCP("SmartStoreToolServer")

# 公共工具：列商品
@mcp.tool()
async def list_products(q: str = "", top_k: int = 5) -> list[dict]:
    async with AsyncSessionLocal() as db:
        items = await crud_product.search_products(db, q, top_k)
    return [
        {"sku": p.sku, "name": p.name,
         "price": p.price_cents / 100, "stock": p.stock}
        for p in items
    ]

# 公共工具：加购物车
@mcp.tool()
async def add_to_cart(user_id: int, sku: str, qty: int = 1) -> dict:
    async with AsyncSessionLocal() as db:
        await crud_cart.add_to_cart(db, user_id, sku, qty)
    return {"ok": True}

# 管理员工具：添加商品
@mcp.tool()
async def add_product(
    token: str,
    sku: str, name: str,
    price_cents: int, stock: int,
    description: str = "", image_url: str | None = None, category_id: int | None = None
) -> str:
    # 1. 验证 Token
    try:
        username = decode_access_token(token)
    except JWTError:
        return json.dumps({"error": "无效或过期 Token"}, ensure_ascii=False)

    async with AsyncSessionLocal() as db:
        user = await get_user_by_username(db, username)
        if not user or not user.is_admin:
            return json.dumps({"error": "管理员权限不足"}, ensure_ascii=False)

        # 2. 尝试创建
        try:
            prod = await crud_product.create_product(
                db,
                ProductCreate(
                    sku=sku, name=name,
                    price_cents=price_cents, stock=stock,
                    description=description,
                    image_url=image_url,
                    category_id=category_id
                )
            )
            payload = {
                "sku": prod.sku,
                "name": prod.name,
                "price": prod.price_cents / 100,
                "stock": prod.stock,
                "description": prod.description,
                "image_url": prod.image_url,
                "category_id": prod.category_id,
            }
            return json.dumps({"ok": True, "product": payload}, ensure_ascii=False)
        except IntegrityError:
            return json.dumps({"error": f"SKU “{sku}” 已存在，请换一个。"}, ensure_ascii=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=args.port,
        path="/mcp",
        log_level="debug",
    )
