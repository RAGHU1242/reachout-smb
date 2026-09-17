from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.models import Lead, Customer, Business, BusinessMember
from app.schemas.schemas import LeadCreate, LeadUpdate, LeadResponse
from app.core.dependencies import get_current_business

router = APIRouter(prefix="/leads", tags=["Lead Management"])

@router.get("", response_model=List[LeadResponse])
async def list_leads(
    status_filter: Optional[str] = None,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Lead, Customer.name)
        .join(Customer, Customer.id == Lead.customer_id)
        .where(Lead.business_id == business.id)
    )
    if status_filter:
        stmt = stmt.where(Lead.status == status_filter)
    stmt = stmt.order_by(Lead.created_at.desc())
    res = await db.execute(stmt)
    rows = res.all()

    leads = []
    for lead, cust_name in rows:
        lead_dict = {
            "id": lead.id,
            "business_id": lead.business_id,
            "customer_id": lead.customer_id,
            "customer_name": cust_name,
            "conversation_id": lead.conversation_id,
            "product_interest": lead.product_interest,
            "budget": lead.budget,
            "purchase_intent": lead.purchase_intent,
            "score": lead.score,
            "status": lead.status,
            "notes": lead.notes,
            "created_at": lead.created_at
        }
        leads.append(LeadResponse(**lead_dict))
    return leads

@router.post("", response_model=LeadResponse)
async def create_lead(
    data: LeadCreate,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    lead = Lead(
        business_id=business.id,
        customer_id=data.customer_id,
        conversation_id=data.conversation_id,
        product_interest=data.product_interest,
        budget=data.budget,
        purchase_intent=data.purchase_intent,
        score=data.score,
        status=data.status,
        notes=data.notes
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    cust_res = await db.execute(select(Customer).where(Customer.id == lead.customer_id))
    cust = cust_res.scalar_one_or_none()

    return LeadResponse(
        id=lead.id,
        business_id=lead.business_id,
        customer_id=lead.customer_id,
        customer_name=cust.name if cust else None,
        conversation_id=lead.conversation_id,
        product_interest=lead.product_interest,
        budget=lead.budget,
        purchase_intent=lead.purchase_intent,
        score=lead.score,
        status=lead.status,
        notes=lead.notes,
        created_at=lead.created_at
    )

@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    data: LeadUpdate,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Lead).where(Lead.id == lead_id, Lead.business_id == business.id)
    res = await db.execute(stmt)
    lead = res.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(lead, k, v)

    await db.commit()
    await db.refresh(lead)

    cust_res = await db.execute(select(Customer).where(Customer.id == lead.customer_id))
    cust = cust_res.scalar_one_or_none()

    return LeadResponse(
        id=lead.id,
        business_id=lead.business_id,
        customer_id=lead.customer_id,
        customer_name=cust.name if cust else None,
        conversation_id=lead.conversation_id,
        product_interest=lead.product_interest,
        budget=lead.budget,
        purchase_intent=lead.purchase_intent,
        score=lead.score,
        status=lead.status,
        notes=lead.notes,
        created_at=lead.created_at
    )
