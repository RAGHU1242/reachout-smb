from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database.session import get_db
from app.models.models import Customer, Business, BusinessMember
from app.models.enums import RoleEnum
from app.schemas.schemas import CustomerCreate, CustomerUpdate, CustomerResponse
from app.core.dependencies import get_current_business, require_roles

router = APIRouter(prefix="/customers", tags=["Customer CRM"])

@router.get("", response_model=List[CustomerResponse])
async def list_customers(
    query: Optional[str] = None,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Customer).where(Customer.business_id == business.id)
    if query:
        q = f"%{query.strip()}%"
        stmt = stmt.where(or_(Customer.name.ilike(q), Customer.phone.ilike(q), Customer.email.ilike(q)))
    stmt = stmt.order_by(Customer.last_interaction.desc())
    res = await db.execute(stmt)
    return [CustomerResponse.model_validate(c) for c in res.scalars().all()]

@router.post("", response_model=CustomerResponse)
async def create_customer(
    data: CustomerCreate,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    cust = Customer(
        business_id=business.id,
        name=data.name,
        phone=data.phone,
        email=data.email,
        preferred_language=data.preferred_language,
        source=data.source,
        tags=data.tags,
        notes=data.notes
    )
    db.add(cust)
    await db.commit()
    await db.refresh(cust)
    return CustomerResponse.model_validate(cust)

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Customer).where(Customer.id == customer_id, Customer.business_id == business.id)
    )
    cust = res.scalar_one_or_none()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerResponse.model_validate(cust)

@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Customer).where(Customer.id == customer_id, Customer.business_id == business.id)
    )
    cust = res.scalar_one_or_none()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(cust, k, v)

    await db.commit()
    await db.refresh(cust)
    return CustomerResponse.model_validate(cust)
