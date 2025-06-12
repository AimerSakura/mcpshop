# mcpshop/services/mcp_client.py
"""
MCPClient  ——  智慧商城客户端 (Stdio + Function-Calling)
-------------------------------------------------------
✦ 环境变量 (建议放 .env)               说明
  ───────────────────────────────────────────────────────
  OPENAI_API_KEY   OpenAI API Key（必填）
  BASE_URL         OpenAI 代理 / 反向代理地址（可选）
  MODEL            默认模型，如 gpt-4o-mini（可选，默认 gpt-4o-mini）
"""

import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from typing import Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI           # 同步 SDK，用 asyncio.to_thread 包装

# ────────────────────────────────
# 环境加载
# ────────────────────────────────
load_dotenv()                       # 读取 .env


class MCPClient:
    """对话客户端：负责
    1. 启动 / 连接 MCP Server (Stdio)
    2. 把可用工具列表交给 OpenAI 进行 Function-Calling
    3. 若触发 tool_calls，则执行并把结果回传给模型
    """

    def __init__(self) -> None:
        self.exit_stack = AsyncExitStack()

        # ── OpenAI 配置 ────────────────────────────────────────────
        self.openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("❌ 未找到 OPENAI_API_KEY，请在 .env 中设置")

        self.base_url: str | None = os.getenv("BASE_URL")  # 代理 / 反代
        self.model: str = os.getenv("MODEL", "gpt-4o-mini")

        # 同步客户端；后续用 asyncio.to_thread 调用避免阻塞事件循环
        self.oa = OpenAI(api_key=self.openai_api_key, base_url=self.base_url)

        # MCP 连接对象
        self.session: Optional[ClientSession] = None
        self.stdio = None            # read_stream
        self.write = None            # write_stream (send)

    # ──────────────────────────────────────────────────────────────
    # 1) 连接 / 启动服务器
    # ──────────────────────────────────────────────────────────────
    async def connect_to_server(self, server_script_path: str) -> None:
        """
        启动（或连接）MCP 服务器脚本（.py / .js 均可）
        """
        ext = os.path.splitext(server_script_path)[1]
        if ext not in {".py", ".js"}:
            raise ValueError("服务器脚本必须是 .py 或 .js 文件!")

        command = "python" if ext == ".py" else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None,                # 继承默认环境变量
        )

        # 启动子进程并建立 stdin/stdout 双流
        self.stdio, self.write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        # 创建 Session
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )
        await self.session.initialize()       # 握手

        # 列出工具
        tools_resp = await self.session.list_tools()
        tool_names = [t.name for t in tools_resp.tools]
        print("✅ 已连接 MCP 服务器，支持工具:", tool_names)

    # ──────────────────────────────────────────────────────────────
    # 2) 处理单轮查询
    # ──────────────────────────────────────────────────────────────
    async def process_query(self, query: str) -> str:
        """
        发给 OpenAI → 解析 tool_calls → 执行工具 → 二次回复
        """
        if self.session is None:
            raise RuntimeError("❌ 未连接到服务器，请先调用 connect_to_server()")

        # 基础对话历史（可扩展为存储上下文）
        messages = [{"role": "user", "content": query}]

        # ── ① 获取工具 schema 列表
        list_resp = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema,  # OpenAI 1.x 需用 parameters/key
                },
            }
            for t in list_resp.tools
        ]

        # ── ② 第一次调用大模型（可能触发工具）
        first_resp = await asyncio.to_thread(
            self.oa.chat.completions.create,
            model=self.model,
            messages=messages,
            tools=available_tools,
        )
        choice = first_resp.choices[0]

        # 未触发工具
        if choice.finish_reason != "tool_calls":
            return choice.message.content

        # ── ③ 若有 tool_calls，执行并回写
        tool_call = choice.message.tool_calls[0]          # 演示只取第一个
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        # 执行工具
        print(f"\n[Tool] → {tool_name} {tool_args}")
        exec_result = await self.session.call_tool(tool_name, tool_args)

        # 把执行结果加入对话
        messages.append(choice.message.model_dump())
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,             # 必需
                "name": tool_name,
                "content": json.dumps(exec_result.content),
            }
        )

        # ── ④ 第二次让模型生成最终回复
        second_resp = await asyncio.to_thread(
            self.oa.chat.completions.create,
            model=self.model,
            messages=messages,
        )
        return second_resp.choices[0].message.content

    # ──────────────────────────────────────────────────────────────
    # 3) 命令行对话循环 (Demo)
    # ──────────────────────────────────────────────────────────────
    async def chat_loop(self) -> None:
        """简单 CLI，输入 quit 退出"""
        print("\n🤖 进入对话，输入 quit 退出。")
        while True:
            try:
                user_in = input("\n你: ").strip()
                if user_in.lower() == "quit":
                    break
                reply = await self.process_query(user_in)
                print(f"\n🤖: {reply}")
            except Exception as exc:
                print(f"\n⚠️ 发生错误: {exc}")

    # ──────────────────────────────────────────────────────────────
    # 4) 资源清理
    # ──────────────────────────────────────────────────────────────
    async def cleanup(self) -> None:
        """退出时关闭所有 async context"""
        await self.exit_stack.aclose()


# ──────────────────────────────────────────────────────────────────
# CLI 入口：python -m mcpshop.services.mcp_client <path_to_server.py>
# ──────────────────────────────────────────────────────────────────
async def _main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m mcpshop.services.mcp_client scripts/mcp_server.py")
        sys.exit(1)

    server_path = sys.argv[1]
    client = MCPClient()

    try:
        await client.connect_to_server(server_path)
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(_main())
