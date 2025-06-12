# mcpshop/db/base.py

from sqlalchemy.orm import declarative_base

# 1. 创建所有 ORM model 的基类
Base = declarative_base()

# 2. （可选）在这里 import 所有 model，确保它们被注册到 Base.metadata
#    这样在运行 Alembic autogenerate 时才能发现所有表
# from mcpshop.models.user import User
# from mcpshop.models.product import Product
# from mcpshop.models.cart_item import CartItem
# ... 依此类推
