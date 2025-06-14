# mcpshop/__init__.py

"""
SmartStore 应用包初始化。

这里将常用的配置和日志器暴露到包级别，方便在项目中直接：
    from mcpshop import settings, logger
而无需每次都写完整路径。
"""
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=r"C:\CodeProject\Pycharm\MCPshop\.env")
# —— 包级别导出 ——
from .core.config import settings
from .core.logger import logger

__all__ = ["settings", "logger"]
