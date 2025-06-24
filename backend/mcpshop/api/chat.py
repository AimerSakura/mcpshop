# -*- coding: utf-8 -*-
"""
Chat API
----------------------------------------------
REST 端点   : POST  /api/chat        （单轮对话）
WebSocket端: WS    /api/chat         （多轮对话）
"""
import os
import json
from pathlib import Path

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
from mcpshop.api.deps import get_current_user, oauth2_scheme
from mcpshop.db.session import get_db
from mcpshop.schemas.chat import ChatRequest
from mcpshop.services.mcp_client import MCPClient
from mcpshop.crud.cart import get_cart_items

# -------------------------------------------------------------------- #
# 环境变量和常量
# -------------------------------------------------------------------- #
load_dotenv(r"C:\CodeProject\Pycharm\MCPshop\.env")
MCP_API_URL: str = os.getenv("MCP_API_URL", "http://127.0.0.1:8001/mcp")

router = APIRouter()

# 单例 MCP 客户端（保持全局，真正使用时再进入 async with）
_ai = MCPClient(MCP_API_URL)

# -------------------------------------------------------------------- #
# REST: POST /api/chat
# -------------------------------------------------------------------- #
@router.post("/api/chat", summary="REST 对话接口")
async def chat_endpoint(
    req: ChatRequest,
    token: str = Depends(oauth2_scheme),
    current=Depends(get_current_user),
):
    """
    单轮对话：直接把用户文本发给 MCP-Server，返回 AI 的结果
    """
    async with _ai.client:
        print("用户token",token)# ★ 关键：开启 fastmcp 会话
        resp = await _ai.process_query(req.text,user_token=token)

    return resp


# -------------------------------------------------------------------- #
# WebSocket: /api/chat
# -------------------------------------------------------------------- #
@router.websocket("/api/chat")
async def websocket_chat(
    ws: WebSocket,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    多轮对话：建立 WebSocket 后循环收发
    """
    await ws.accept()

    # 整个 WebSocket 生命周期只进入一次 async with，
    # 避免每条消息都重新连接 MCP-Server
    async with _ai.client:                      # ★ 关键：开启 fastmcp 会话
        try:
            while True:
                text = await ws.receive_text()
                answer = await _ai.process_query(text, user_token=token)

                # answer 可能是纯字符串，也可能已是 JSON 字符串/字典
                if isinstance(answer, str):
                    try:
                        answer = json.loads(answer)
                    except json.JSONDecodeError:
                        answer = {"reply": answer, "actions": []}

                cart = await get_cart_items(db, user.user_id)

                await ws.send_json(
                    {
                        "reply":   answer.get("reply", ""),
                        "actions": answer.get("actions", []),
                        "cart":    cart,
                    }
                )
        except WebSocketDisconnect:
            # 客户端正常关闭
            pass
        except Exception as e:
            # 其它异常转换为 500
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"WebSocket 对话出错：{e}",
            )