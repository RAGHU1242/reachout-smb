from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database.session import get_db
from app.models.models import Product, ProductCategory, ProductImage, Business, BusinessMember
from app.models.enums import RoleEnum
from app.schemas.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductCategoryCreate, ProductCategoryResponse
)
from app.core.dependencies import get_current_business, require_roles

router = APIRouter(prefix="/products", tags=["Product Catalogue"])

@router.get("", response_model=List[ProductResponse])
async def list_products(
    category_id: Optional[str] = None,
    query: Optional[str] = None,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Product).where(Product.business_id == business.id)
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    if query:
        q = f"%{query.strip()}%"
        stmt = stmt.where(or_(Product.name.ilike(q), Product.sku.ilike(q), Product.color.ilike(q)))
    stmt = stmt.order_by(Product.created_at.desc())
    res = await db.execute(stmt)
    products = res.scalars().all()
    return [ProductResponse.model_validate(p) for p in products]

@router.post("", response_model=ProductResponse)
async def create_product(
    data: ProductCreate,
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.STAFF])),
    db: AsyncSession = Depends(get_db)
):
    product = Product(
        business_id=business.id,
        name=data.name,
        description=data.description,
        price=data.price,
        compare_at_price=data.compare_at_price,
        sku=data.sku,
        stock=data.stock,
        active=data.active,
        category_id=data.category_id,
        tags=data.tags,
        color=data.color,
        size=data.size,
        attributes=data.attributes
    )
    db.add(product)
    await db.flush()

    for idx, img_url in enumerate(data.images):
        img = ProductImage(
            product_id=product.id,
            image_url=img_url,
            is_primary=(idx == 0),
            sort_order=idx
        )
        db.add(img)

    await db.commit()
    await db.refresh(product)
    return ProductResponse.model_validate(product)

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Product).where(Product.id == product_id, Product.business_id == business.id)
    )
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    data: ProductUpdate,
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.STAFF])),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Product).where(Product.id == product_id, Product.business_id == business.id)
    )
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(product, k, v)

    await db.commit()
    await db.refresh(product)
    return ProductResponse.model_validate(product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Product).where(Product.id == product_id, Product.business_id == business.id)
    )
    product = res.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(product)
    await db.commit()
    return None

# Categories
@router.get("/categories/all", response_model=List[ProductCategoryResponse])
async def list_categories(
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(ProductCategory).where(ProductCategory.business_id == business.id)
    )
    cats = res.scalars().all()
    return [ProductCategoryResponse.model_validate(c) for c in cats]

@router.post("/categories", response_model=ProductCategoryResponse)
async def create_category(
    data: ProductCategoryCreate,
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN, RoleEnum.STAFF])),
    db: AsyncSession = Depends(get_db)
):
    slug = data.slug or data.name.lower().replace(" ", "-")
    cat = ProductCategory(
        business_id=business.id,
        name=data.name,
        slug=slug,
        description=data.description
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return ProductCategoryResponse.model_validate(cat)
