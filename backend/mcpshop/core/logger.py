# mcpshop/core/logger.py
from loguru import logger
import sys

# 移除默认的 logger，以便自定义配置
logger.remove()

# 添加一个 stdout 日志器，INFO 及以上级别
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{line}</cyan> - {message}"
)

# 如果需要写入文件，也可以：
# logger.add("logs/app_{time:YYYY-MM-DD}.log", rotation="00:00", level="INFO")

# 在项目任何地方直接：
# from mcpshop.core.logger import logger
# logger.info("应用启动")
