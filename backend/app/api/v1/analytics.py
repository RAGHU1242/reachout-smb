from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database.session import get_db
from app.models.models import Order, Lead, Conversation, Business, Customer, OrderItem
from app.models.enums import OrderStatus, LeadStatus, ConversationStatus
from app.schemas.schemas import AnalyticsOverview, OrderResponse, LeadResponse, OrderItemResponse
from app.core.dependencies import get_current_business

router = APIRouter(prefix="/analytics", tags=["Analytics & Insights"])

@router.get("/overview", response_model=AnalyticsOverview)
async def get_overview(
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    # Total revenue & orders
    rev_res = await db.execute(
        select(func.sum(Order.total), func.count(Order.id))
        .where(Order.business_id == business.id, Order.status != OrderStatus.CANCELLED.value)
    )
    rev_row = rev_res.first()
    total_rev = float(rev_row[0] or 0.0)
    total_orders = int(rev_row[1] or 0)

    # Leads counts
    new_leads_res = await db.execute(
        select(func.count(Lead.id)).where(Lead.business_id == business.id, Lead.status == LeadStatus.NEW.value)
    )
    new_leads = int(new_leads_res.scalar() or 0)

    hot_leads_res = await db.execute(
        select(func.count(Lead.id)).where(Lead.business_id == business.id, Lead.status == LeadStatus.HOT.value)
    )
    hot_leads = int(hot_leads_res.scalar() or 0)

    # Conversations
    conv_tot_res = await db.execute(
        select(func.count(Conversation.id)).where(Conversation.business_id == business.id)
    )
    tot_conv = int(conv_tot_res.scalar() or 0)

    ai_handled_res = await db.execute(
        select(func.count(Conversation.id)).where(Conversation.business_id == business.id, Conversation.is_ai_handled == True)
    )
    ai_handled = int(ai_handled_res.scalar() or 0)

    handoff_res = await db.execute(
        select(func.count(Conversation.id)).where(Conversation.business_id == business.id, Conversation.is_ai_handled == False)
    )
    handoff_count = int(handoff_res.scalar() or 0)

    # Conversion rate
    conversion_rate = round((total_orders / tot_conv * 100), 1) if tot_conv > 0 else 0.0
    ai_rate = round((ai_handled / tot_conv * 100), 1) if tot_conv > 0 else 100.0

    # Recent orders
    ord_stmt = (
        select(Order, Customer.name)
        .join(Customer, Customer.id == Order.customer_id)
        .where(Order.business_id == business.id)
        .order_by(Order.created_at.desc())
        .limit(5)
    )
    ord_rows = (await db.execute(ord_stmt)).all()
    recent_orders = []
    for o, c_name in ord_rows:
        items_res = await db.execute(select(OrderItem).where(OrderItem.order_id == o.id))
        items = items_res.scalars().all()
        recent_orders.append(OrderResponse(
            id=o.id,
            business_id=o.business_id,
            customer_id=o.customer_id,
            customer_name=c_name,
            order_number=o.order_number,
            status=o.status,
            subtotal=o.subtotal,
            delivery_fee=o.delivery_fee,
            discount=o.discount,
            total=o.total,
            delivery_address=o.delivery_address,
            payment_status=o.payment_status,
            created_at=o.created_at,
            items=[OrderItemResponse.model_validate(it) for it in items]
        ))

    # Hot leads
    lead_stmt = (
        select(Lead, Customer.name)
        .join(Customer, Customer.id == Lead.customer_id)
        .where(Lead.business_id == business.id, Lead.status == LeadStatus.HOT.value)
        .order_by(Lead.score.desc())
        .limit(5)
    )
    lead_rows = (await db.execute(lead_stmt)).all()
    hot_leads_list = [
        LeadResponse(
            id=l.id,
            business_id=l.business_id,
            customer_id=l.customer_id,
            customer_name=c_name,
            conversation_id=l.conversation_id,
            product_interest=l.product_interest,
            budget=l.budget,
            purchase_intent=l.purchase_intent,
            score=l.score,
            status=l.status,
            notes=l.notes,
            created_at=l.created_at
        ) for l, c_name in lead_rows
    ]

    return AnalyticsOverview(
        total_revenue=total_rev,
        total_orders=total_orders,
        new_leads=new_leads,
        hot_leads=hot_leads,
        total_conversations=tot_conv,
        ai_handled_count=ai_handled,
        human_handoff_count=handoff_count,
        conversion_rate=conversion_rate,
        ai_handling_rate=ai_rate,
        recent_orders=recent_orders,
        hot_leads_list=hot_leads_list
    )
