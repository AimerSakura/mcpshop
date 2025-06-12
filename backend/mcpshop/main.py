# mcpshop/main.py
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
    uvicorn.run("mcpshop.main:app", host="0.0.0.0", port=8000, reload=True)
