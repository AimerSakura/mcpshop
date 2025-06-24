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
from sqlalchemy import text
from sqlalchemy import select
from mcpshop.models.user import User
from sqlalchemy import select
from mcpshop.models.order import Order
from typing import Optional
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

#管理员工具：列全部用户
@mcp.tool()
async def list_users(token: str) -> str:
    try:
        username = decode_access_token(token)
    except JWTError:
        return json.dumps({"error": "无效或过期 Token"}, ensure_ascii=False)
    async with AsyncSessionLocal() as db:
        user = await get_user_by_username(db, username)
        if not user or not user.is_admin:
            return json.dumps({"error": "管理员权限不足"}, ensure_ascii=False)
        # ORM查询所有用户
        result = await db.execute(select(User))
        users = result.scalars().all()
        return json.dumps([{
            "user_id": u.user_id, "username": u.username, "email": u.email, "is_admin": u.is_admin
        } for u in users], ensure_ascii=False)

#管理员工具：删除用户
@mcp.tool()
async def delete_user(token: str, username: str) -> str:
    # 校验管理员token
    try:
        admin_username = decode_access_token(token)
    except JWTError:
        return json.dumps({"error": "无效或过期 Token"}, ensure_ascii=False)

    async with AsyncSessionLocal() as db:
        admin_user = await get_user_by_username(db, admin_username)
        if not admin_user or not admin_user.is_admin:
            return json.dumps({"error": "管理员权限不足"}, ensure_ascii=False)

        # 不允许管理员删除自己
        if admin_username == username:
            return json.dumps({"error": "不能删除自己的管理员账号"}, ensure_ascii=False)

        user = await get_user_by_username(db, username)
        if not user:
            return json.dumps({"error": "用户不存在"}, ensure_ascii=False)
        await db.delete(user)
        await db.commit()
        return json.dumps({"ok": True, "deleted_user": username}, ensure_ascii=False)

@mcp.tool()
async def list_all_orders(token: Optional[str] = None) -> str:   # ✅ 可选
    # —— 1. 补 token，如果后端没注入就报错 ——
    if not token:       # None 或空串都算未注入
        return json.dumps({"error": "缺少管理员 Token"}, ensure_ascii=False)

    # —— 2. 校验 token ——        （原逻辑不变）
    try:
        username = decode_access_token(token)
    except JWTError:
        return json.dumps({"error": "无效或过期 Token"}, ensure_ascii=False)

    async with AsyncSessionLocal() as db:
        user = await get_user_by_username(db, username)
        if not user or not user.is_admin:
            return json.dumps({"error": "管理员权限不足"}, ensure_ascii=False)

        result = await db.execute(select(Order))          # ORM 写法更稳
        orders  = result.scalars().all()
        payload = [{
            "order_id":    o.order_id,
            "user_id":     o.user_id,
            "total_cents": o.total_cents,
            "status":      o.status.value,
            "created_at":  o.created_at.isoformat(),
        } for o in orders]

        return json.dumps(payload, ensure_ascii=False)


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
