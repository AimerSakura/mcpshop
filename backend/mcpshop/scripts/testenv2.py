import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv(dotenv_path=r"C:\CodeProject\Pycharm\MCPshop\.env")  # 显式指定路径

# 打印加载的环境变量，确保它们已被正确加载
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("REDIS_URL:", os.getenv("REDIS_URL"))
print("JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))
print("MCP_API_URL:", os.getenv("MCP_API_URL"))
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
