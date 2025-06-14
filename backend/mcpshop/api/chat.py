# backend/mcpshop/api/chat.py

import os
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from mcpshop.api.deps      import get_current_user
from mcpshop.db.session    import get_db
from mcpshop.schemas.chat  import ChatRequest
from mcpshop.services.mcp_client import MCPClient
from mcpshop.crud.cart     import get_cart_items

# 1. 加载环境变量并读取 MCP 服务地址
load_dotenv(dotenv_path=r"C:\CodeProject\Pycharm\MCPshop\.env")
MCP_API_URL = os.getenv("MCP_API_URL", "http://127.0.0.1:8000/mcp")

router = APIRouter()

# ------------------------------------------------------------------
# 共用一个 MCPClient；首次使用时再启动/连接本地 MCP Server
# ------------------------------------------------------------------
_ai = MCPClient(MCP_API_URL)   # ← 这里传入 server_url，就不会再报错了

_SERVER_SCRIPT = str(
    Path(__file__)
    .resolve()
    .parents[2]  # 回到项目根/backend/mcpshop/scripts
    / "scripts"
    / "mcp_server.py"
)

async def _ensure_ai_ready() -> None:
    if _ai.session is None:
        await _ai.connect_to_server(_SERVER_SCRIPT)

# ------------------------------------------------------------------
# 1) REST 端点：POST /api/chat
# ------------------------------------------------------------------
@router.post("/api/chat", summary="REST 对话接口")
async def chat_endpoint(
    req: ChatRequest,
    current=Depends(get_current_user),
):
    """
    请求体： {"text": "."}
    返回：   {"reply": ".", "actions":[.]}
    """
    await _ensure_ai_ready()
    result = await _ai.process_query(req.text)
    return result

# ------------------------------------------------------------------
# 2) WebSocket：/api/chat
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
            result = await _ai.process_query(text)
            cart_items = await get_cart_items(db, user.user_id)
            await ws.send_json({
                "reply": result["reply"],
                "actions": result.get("actions", []),
                "cart": cart_items,
            })
    except WebSocketDisconnect:
        pass
