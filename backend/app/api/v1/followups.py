from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.models import FollowUpJob, Customer, Business
from app.schemas.schemas import FollowUpCreate, FollowUpResponse
from app.core.dependencies import get_current_business

router = APIRouter(prefix="/followups", tags=["Follow-Up Automation"])

@router.get("", response_model=List[FollowUpResponse])
async def list_followups(
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(FollowUpJob, Customer.name)
        .join(Customer, Customer.id == FollowUpJob.customer_id)
        .where(FollowUpJob.business_id == business.id)
        .order_by(FollowUpJob.scheduled_at.asc())
    )
    res = await db.execute(stmt)
    rows = res.all()

    jobs = []
    for job, cust_name in rows:
        jobs.append(FollowUpResponse(
            id=job.id,
            business_id=job.business_id,
            customer_id=job.customer_id,
            customer_name=cust_name,
            conversation_id=job.conversation_id,
            scheduled_at=job.scheduled_at,
            channel=job.channel,
            message=job.message,
            reason=job.reason,
            status=job.status,
            created_at=job.created_at
        ))
    return jobs

@router.post("", response_model=FollowUpResponse)
async def create_followup(
    data: FollowUpCreate,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    job = FollowUpJob(
        business_id=business.id,
        customer_id=data.customer_id,
        conversation_id=data.conversation_id,
        scheduled_at=data.scheduled_at,
        channel=data.channel,
        message=data.message,
        reason=data.reason,
        status="SCHEDULED"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    cust_res = await db.execute(select(Customer).where(Customer.id == job.customer_id))
    cust = cust_res.scalar_one_or_none()

    return FollowUpResponse(
        id=job.id,
        business_id=job.business_id,
        customer_id=job.customer_id,
        customer_name=cust.name if cust else None,
        conversation_id=job.conversation_id,
        scheduled_at=job.scheduled_at,
        channel=job.channel,
        message=job.message,
        reason=job.reason,
        status=job.status,
        created_at=job.created_at
    )
