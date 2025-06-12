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
