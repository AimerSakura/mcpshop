from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from mcpshop.db.session import get_db
from mcpshop.schemas.product import ProductCreate, ProductOut, ProductUpdate
from mcpshop.crud.product import (
    create_product, get_product_by_sku, search_products,
    )

router = APIRouter(prefix="/api/products", tags=["products"])

@router.post("/", response_model=ProductOut)
async def create(p: ProductCreate, db: AsyncSession = Depends(get_db)):
    exists = await get_product_by_sku(db, p.sku)
    if exists:
        raise HTTPException(status_code=400, detail="SKU 已存在")
    return await create_product(db, p)

@router.get("/", response_model=List[ProductOut])
async def list_products(
    q: str = Query("", description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    return await search_products(db, q, limit)

@router.get("/{sku}", response_model=ProductOut)
async def get_sku(
    sku: str, db: AsyncSession = Depends(get_db)
):
    prod = await get_product_by_sku(db, sku)
    if not prod:
        raise HTTPException(status_code=404, detail="未找到商品")
    return prod

@router.patch("/{sku}", response_model=ProductOut)
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

@router.delete("/{sku}", status_code=204)
async def delete_sku(
    sku: str, db: AsyncSession = Depends(get_db)
):
    prod = await get_product_by_sku(db, sku)
    if not prod:
        raise HTTPException(status_code=404, detail="未找到商品")
    await db.delete(prod)
    await db.commit()
