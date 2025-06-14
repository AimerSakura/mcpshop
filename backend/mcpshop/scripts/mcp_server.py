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
