# 文件：backend/mcpshop/services/mcp_client.py

import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from fastmcp import Client
from openai import OpenAI

# 1. 载入 .env
load_dotenv(r"C:\CodeProject\Pycharm\MCPshop\.env")

class MCPClient:
    """基于 HTTP 的 MCP demo 客户端"""

    def __init__(self, server_url: str):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ 请在 .env 中设置 OPENAI_API_KEY")
        self.oa = OpenAI(api_key=api_key, base_url=os.getenv("BASE_URL") or None)
        self.model = os.getenv("MODEL", "deepseek-chat")

        # —— 读取管理员 Token ——
        self.admin_token = os.getenv("ADMIN_TOKEN")
        if not self.admin_token:
            raise ValueError("❌ 请在 .env 中设置 ADMIN_TOKEN")

        # fastmcp HTTP 客户端
        self.client = Client(server_url)

    # ------------------------- 核心逻辑 -------------------------

    async def process_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]

        # ① 拉取工具列表并构造 funcs schema
        tools = await self.client.list_tools()
        func_schemas = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": getattr(tool, "inputSchema", getattr(tool, "input_schema", {})),
                },
            }
            for tool in tools
        ]

        # ② 首轮推理
        first = await asyncio.to_thread(
            self.oa.chat.completions.create,
            model=self.model,
            messages=messages,
            tools=func_schemas,
        )
        choice = first.choices[0]

        if choice.finish_reason != "tool_calls":
            return choice.message.content

        # ③ 执行工具
        tc = choice.message.tool_calls[0]
        tool_name = tc.function.name
        tool_args = json.loads(tc.function.arguments)

        # —— 如果是 add_product，自动注入管理员 token ——
        if tool_name == "add_product":
            tool_args.setdefault("token", self.admin_token)

        print(f"[调用工具] {tool_name} {tool_args}")
        exec_res = await self.client.call_tool(tool_name, tool_args)
        result_content = getattr(exec_res, "content", exec_res)

        # ④ 把工具结果写回对话，再次推理
        messages.append(choice.message.model_dump())
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "name": tool_name,
            "content": json.dumps(result_content, ensure_ascii=False),
        })

        second = await asyncio.to_thread(
            self.oa.chat.completions.create,
            model=self.model,
            messages=messages,
        )
        return second.choices[0].message.content

    # ------------------------- CLI 对话循环 -------------------------

    async def chat_loop(self):
        print("🤖 进入对话（HTTP 模式），输入 quit 退出")
        while True:
            prompt = input("你: ").strip()
            if prompt.lower() == "quit":
                break
            try:
                resp = await self.process_query(prompt)
                print("🤖:", resp)
            except Exception as e:
                print("⚠️ 出错:", e)

    async def run(self):
        async with self.client as client:
            try:
                await client.ping()
                print("✅ MCP Server 握手成功，开始对话")
            except Exception as e:
                print("❌ 握手失败，请检查 URL 或服务状态：", e)
                return
            await self.chat_loop()

# ------------------------- 入口 -------------------------

async def _main():
    if len(sys.argv) != 2:
        print("用法: python -m mcpshop.services.mcp_client <http://host:port/mcp>")
        sys.exit(1)
    url = sys.argv[1]
    client = MCPClient(url)
    await client.run()

if __name__ == "__main__":
    asyncio.run(_main())
