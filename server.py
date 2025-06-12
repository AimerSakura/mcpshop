# server.py
"""
Demo MCP Server
---------------
✦ 两种启动方式：
   • STDIO 模式：   python server.py --stdio
   • HTTP 模式：    python server.py --port 8001
"""

import argparse
from typing import List

# 使用新版 fastmcp（≥2.0）
from fastmcp import FastMCP

# 初始化 MCP
mcp = FastMCP("Demo")


# ---------- 工具（Tools） -----------------------------------------
@mcp.tool()
def add(a: int, b: int) -> int:
    """加法"""
    return a + b

@mcp.tool()
def sub(a: int, b: int) -> int:
    """减法"""
    return a - b


# ---------- 资源（Resource） ---------------------------------------
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """根据 name 返回问候字符串"""
    return f"Hello, {name}!"


# ---------- 启动入口（Run） ---------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo MCP Server")
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="以 STDIO 模式启动（嵌入式，供 Inspector 或其它客户端用）"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="HTTP 服务端口（默认 8001）"
    )
    args = parser.parse_args()

    if args.stdio:
        # 嵌入式模式：Inspector 可以用 stdio 直接交互
        mcp.run(transport="stdio")
    else:
        # HTTP 模式：Inspector 也支持 streamable-http
        mcp.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=args.port,
            log_level="info",
        )
