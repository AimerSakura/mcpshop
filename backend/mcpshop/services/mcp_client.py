import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from fastmcp import Client
from openai import OpenAI

# 强制加载并覆盖环境变量
load_dotenv(r"C:\CodeProject\Pycharm\MCPshop\.env", override=True)

class MCPClient:
    """基于 fastmcp 的 CLI 客户端，所有返回数据用 LLM 过滤成 JSON"""

    def __init__(self, server_url: str):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 中设置 OPENAI_API_KEY")
        self.oa = OpenAI(api_key=api_key, base_url=os.getenv("BASE_URL") or None)
        self.model = os.getenv("MODEL", "deepseek-chat")

        # 解析模型，用于从文本中提取JSON
        self.parser_oa = OpenAI(api_key=api_key, base_url=os.getenv("BASE_URL") or None)
        self.parser_model = "deepseek-chat"

        self.client = Client(server_url.rstrip("/"))

    async def _extract_json(self, text: str) -> str:
        """
        用 GPT-4 从文本中提取严格的 JSON 对象并返回。
        """
        messages = [
            {"role": "system", "content": "你是一个 JSON 提取器，只输出严格的 JSON，不要额外解释。"},
            {"role": "user", "content": f"请从下面内容中提取 JSON：\n```\n{text}\n```"}
        ]
        resp = await asyncio.to_thread(
            self.parser_oa.chat.completions.create,
            model=self.parser_model,
            messages=messages
        )
        return resp.choices[0].message.content.strip()

    async def process_query(self, query: str, user_token: str = "") -> str:
        # 1. 用户消息
        messages = [{"role": "user", "content": query}]

        # 2. 拉取工具 schema
        tools = await self.client.list_tools()
        func_schemas = [{
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": getattr(t, "inputSchema", getattr(t, "input_schema", {})),
            }
        } for t in tools]

        # 3. 首轮推理
        first = await asyncio.to_thread(
            self.oa.chat.completions.create,
            model=self.model,
            messages=messages,
            tools=func_schemas,
        )
        choice = first.choices[0]
        if choice.finish_reason != "tool_calls":
            return choice.message.content

        # 4. 执行工具
        tc = choice.message.tool_calls[0]
        tool_name = tc.function.name
        tool_args = json.loads(tc.function.arguments)
        # 关键修正点：始终用当前用户token
        if tool_name == "add_product":
            tool_args["token"] = user_token  # 不再写死ADMIN_TOKEN

        print(f"[调用工具] {tool_name} {tool_args}")
        res = await self.client.call_tool(tool_name, tool_args)

        # 5. 统一提取“文本结果”
        # 支持：TextContent、ToolResponse、dict/list、纯 str
        if hasattr(res, "text"):
            # fastmcp 的 TextContent
            result_text = res.text
        elif hasattr(res, "content"):
            content = res.content
            if isinstance(content, (dict, list)):
                result_text = json.dumps(content, ensure_ascii=False)
            else:
                result_text = str(content)
        else:
            result_text = str(res)

        # 6. 用 GPT-4 清洗 JSON
        clean_text = await self._extract_json(result_text)

        return clean_text

    async def chat_loop(self, user_token: str = ""):
        print("🤖 进入对话（HTTP 模式），输入 quit 退出")
        while True:
            prompt = input("你: ").strip()
            if prompt.lower() == "quit":
                break
            try:
                resp = await self.process_query(prompt, user_token=user_token)
                # 尝试解析 JSON
                try:
                    j = json.loads(resp)
                    print("🤖", json.dumps(j, ensure_ascii=False, indent=2))
                except json.JSONDecodeError:
                    print("🤖:", resp)
            except Exception as e:
                print("⚠️ 出错:", e)

    async def run(self, user_token: str = ""):
        async with self.client:
            try:
                await self.client.ping()
                print("✅ MCP Server 握手成功")
            except Exception as e:
                print("❌ 无法连接 MCP Server：", e)
                return
            await self.chat_loop(user_token=user_token)

async def _main():
    if len(sys.argv) < 2:
        print("用法: python -m mcpshop.services.mcp_client <http://host:port/mcp> [user_token]")
        sys.exit(1)
    server_url = sys.argv[1]
    user_token = sys.argv[2] if len(sys.argv) > 2 else ""
    await MCPClient(server_url).run(user_token=user_token)

if __name__ == "__main__":
    asyncio.run(_main())
