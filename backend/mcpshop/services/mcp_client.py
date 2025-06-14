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

        # OpenAI 同步 SDK（包装到线程池里）
        self.oa = OpenAI(api_key=api_key, base_url=os.getenv("BASE_URL") or None)
        self.model = os.getenv("MODEL", "deepseek-chat")

        # fastmcp HTTP 客户端
        self.client = Client(server_url)

    # ------------------------- 核心逻辑 -------------------------

    async def process_query(self, query: str) -> str:
        """向 LLM 发送消息，必要时自动调用 MCP 工具"""
        messages = [{"role": "user", "content": query}]

        # ① 向服务器拉取全部工具 schema
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

        # ② 首轮推理（可能触发 tool_calls）
        first = await asyncio.to_thread(
            self.oa.chat.completions.create,
            model=self.model,
            messages=messages,
            tools=func_schemas,
        )
        choice = first.choices[0]

        # 无 tool_call：直接返回文本
        if choice.finish_reason != "tool_calls":
            return choice.message.content

        # ③ 执行一次工具
        tc = choice.message.tool_calls[0]
        tool_name = tc.function.name
        tool_args = json.loads(tc.function.arguments)
        print(f"[调用工具] {tool_name} {tool_args}")

        exec_res = await self.client.call_tool(tool_name, tool_args)

        # fastmcp ≥0.4 直接返回原始结果；旧版返回带 .content 的对象
        result_content = getattr(exec_res, "content", exec_res)

        # ④ 把工具结果写回对话，再次推理
        messages.append(choice.message.model_dump())
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tool_name,
                # OpenAI 要求 string，所以先转 JSON 字符串
                "content": json.dumps(result_content, ensure_ascii=False),
            }
        )

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
