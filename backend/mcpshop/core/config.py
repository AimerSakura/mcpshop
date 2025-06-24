# mcpshop/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl


class Settings(BaseSettings):
    # —— 项目基础信息 ——  
    PROJECT_NAME: str = "SmartStore"
    VERSION: str = "0.1.0"

    # —— 数据库 & 缓存 ——  
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # —— JWT ——  
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180

    # —— MCP Server ——  
    MCP_API_URL: AnyUrl = Field(..., env="MCP_API_URL")
    MCP_API_KEY: str | None = Field(None, env="MCP_API_KEY")

    # —— OpenAI / MCPClient ——  
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    BASE_URL: str | None = Field(None, env="BASE_URL")
    MODEL: str = Field("deepseek-reasoner", env="MODEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"       # 忽略 .env 中多余未经声明的变量


# 在模块顶层实例化
settings = Settings()
