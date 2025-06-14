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
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\CodeProject\Pycharm\MCPshop\.env")

# 验证环境变量是否正确加载
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("REDIS_URL:", os.getenv("REDIS_URL"))
print("JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))
print("MCP_API_URL:", os.getenv("MCP_API_URL"))
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
from typing import List
import asyncio
import argparse

from mcp.server.fastmcp import FastMCP
from mcpshop.crud import product as crud_product, cart as crud_cart
from mcpshop.db.session import get_db
from dotenv import load_dotenv


# 加载环境变量



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
@mcp.resource("mcpshop://products_all")
async def products_all() -> List[dict]:
    """暴露全量商品信息作为 Resource"""
    async with get_db() as db:
        items = await crud_product.list_all_products(db)
    return [
        {"sku": p.sku, "name": p.name, "price": p.price_cents / 100}
        for p in items
    ]
# ---------- Run ----------------------------------------------------

# ---------- Run ----------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--stdio", action="store_true", help="Serve via stdio")
    parser.add_argument("--port", type=int, default=8001, help="HTTP port")
    args = parser.parse_args()

    if args.stdio:
        # 嵌入式模式：走 STDIO（ClientSession 会拉起）
        import asyncio
        asyncio.run(mcp.serve_stdio())
    else:
        # FastMCP 官方推荐的 HTTP 模式
        # transport="streamable-http" ⇒ 普通 HTTP + SSE
        # 如果想最小依赖，也可以 transport="http"
        mcp.run(
            transport="streamable-http",
            # host="0.0.0.0",
            # port=args.port,
            # log_level="info",
        )
