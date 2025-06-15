from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.db.session import get_db
from mcpshop.schemas.product import ProductCreate, ProductOut, ProductUpdate
from mcpshop.crud.product import (
    create_product, get_product_by_sku, search_products,
)

# ★ 新增管理员依赖
from mcpshop.api.deps import get_current_admin_user

router = APIRouter(prefix="/api/products", tags=["products"])

# ★ 管理员才能添加商品
@router.post("/", response_model=ProductOut, dependencies=[Depends(get_current_admin_user)])
async def create(
    p: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    exists = await get_product_by_sku(db, p.sku)
    if exists:
        raise HTTPException(status_code=400, detail="SKU 已存在")
    return await create_product(db, p)

# 所有人都能查看商品列表
@router.get("/", response_model=List[ProductOut])
async def list_products(
    q: str = Query("", description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await search_products(db, q, limit)

# 所有人都能查商品详情
@router.get("/{sku}", response_model=ProductOut)
async def get_sku(
    sku: str, db: AsyncSession = Depends(get_db)
):
    prod = await get_product_by_sku(db, sku)
    if not prod:
        raise HTTPException(status_code=404, detail="未找到商品")
    return prod

# ★ 管理员才能修改商品
@router.patch("/{sku}", response_model=ProductOut, dependencies=[Depends(get_current_admin_user)])
async def update_sku(
    sku: str,
    p: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    prod = await get_product_by_sku(db, sku)
    if not prod:
        raise HTTPException(status_code=404, detail="未找到商品")
    for k, v in p.dict(exclude_unset=True).items():
        setattr(prod, k, v)
    await db.commit()
    await db.refresh(prod)
    return prod

# ★ 管理员才能删除商品
@router.delete("/{sku}", status_code=204, dependencies=[Depends(get_current_admin_user)])
async def delete_sku(
    sku: str, db: AsyncSession = Depends(get_db)
):
    prod = await get_product_by_sku(db, sku)
    if not prod:
        raise HTTPException(status_code=404, detail="未找到商品")
    await db.delete(prod)
    await db.commit()
