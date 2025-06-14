# 文件：backend/mcpshop/main.py

import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\CodeProject\Pycharm\MCPshop\.env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcpshop.core.config      import settings
from mcpshop.api              import auth, cart, chat, orders, products
from mcpshop.db.session       import engine
from mcpshop.db.base          import Base
from mcpshop.scripts.mcp_server import mcp

import uvicorn

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION
    )
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # —— 公共 REST API 路由 ——
    # 这些 router 在各自文件里已声明了 prefix="/api/xxx"
    app.include_router(auth.router)
    app.include_router(cart.router)
    app.include_router(chat.router)
    app.include_router(orders.router)
    app.include_router(products.router)

    # —— 将所有 MCP 工具挂载到 /mcp ——
    app.mount("/mcp", mcp)

    @app.on_event("startup")
    async def on_startup() -> None:
        # **开发演示**：自动建表。生产请使用 Alembic。
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("mcpshop.main:app", host="127.0.0.1", port=8000, reload=True)
