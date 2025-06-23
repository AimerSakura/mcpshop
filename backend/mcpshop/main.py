import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\CodeProject\Pycharm\MCPshop\.env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcpshop.core.config import settings
from mcpshop.api import auth, cart, chat, orders, products, users  # ★ 新增 users
from mcpshop.db.session import engine
from mcpshop.db.base import Base

import uvicorn

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION
    )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- 业务 REST 路由（各自模块已包含 prefix） ---
    app.include_router(auth.router)
    app.include_router(cart.router)
    app.include_router(chat.router)
    app.include_router(orders.router)
    app.include_router(products.router)
    app.include_router(users.router)  # ★ 新增注册 users 路由

    # --- 启动时自动建表（演示用，生产请用 Alembic） ---
    @app.on_event("startup")
    async def on_startup() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("mcpshop.main:app", host="0.0.0.0", port=8000, reload=True)
