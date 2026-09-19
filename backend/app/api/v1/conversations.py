from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.models import Conversation, Message, Customer, Business, BusinessMember, Lead, Order
from app.models.enums import ConversationStatus, MessageSenderType
from app.schemas.schemas import (
    ConversationResponse, MessageCreate, MessageResponse, HumanHandoffRequest
)
from app.core.dependencies import get_current_business
from app.integrations.instagram_provider import MetaInstagramProvider
from app.integrations.whatsapp_provider import MetaWhatsAppCloudProvider

router = APIRouter(prefix="/conversations", tags=["Unified Conversations"])

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    channel: Optional[str] = None,
    status_filter: Optional[str] = None,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Conversation, Customer.name, Customer.phone, Customer.preferred_language)
        .join(Customer, Customer.id == Conversation.customer_id)
        .where(Conversation.business_id == business.id)
    )
    if channel:
        stmt = stmt.where(Conversation.channel == channel)
    if status_filter:
        stmt = stmt.where(Conversation.status == status_filter)

    stmt = stmt.order_by(Conversation.last_message_at.desc())
    res = await db.execute(stmt)
    rows = res.all()

    convs = []
    for conv, c_name, c_phone, pref_lang in rows:
        # Get latest message
        m_res = await db.execute(
            select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at.desc()).limit(1)
        )
        latest = m_res.scalar_one_or_none()

        # Get associated lead
        lead_res = await db.execute(
            select(Lead).where(
                (Lead.conversation_id == conv.id) | (Lead.customer_id == conv.customer_id)
            ).order_by(Lead.created_at.desc()).limit(1)
        )
        lead = lead_res.scalar_one_or_none()

        # Get recent order for delivery context
        ord_res = await db.execute(
            select(Order).where(Order.customer_id == conv.customer_id).order_by(Order.created_at.desc()).limit(1)
        )
        recent_ord = ord_res.scalar_one_or_none()

        conv_dict = {
            "id": conv.id,
            "business_id": conv.business_id,
            "customer_id": conv.customer_id,
            "customer_name": c_name,
            "customer_phone": c_phone,
            "channel": conv.channel,
            "status": conv.status,
            "is_ai_handled": conv.is_ai_handled,
            "handoff_reason": conv.handoff_reason,
            "last_message_at": conv.last_message_at,
            "created_at": conv.created_at,
            "latest_message": MessageResponse.model_validate(latest) if latest else None,
            "preferred_language": pref_lang,
            "lead_score": lead.score if lead else None,
            "lead_status": lead.status if lead else None,
            "lead_product_interest": lead.product_interest if lead else None,
            "lead_budget": lead.budget if lead else None,
            "lead_notes": lead.notes if lead else None,
            "delivery_locality": recent_ord.delivery_address if recent_ord else None,
            "delivery_fee": recent_ord.delivery_fee if recent_ord else None
        }
        convs.append(ConversationResponse(**conv_dict))

    return convs

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    # Verify conversation ownership
    c_res = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.business_id == business.id)
    )
    if not c_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
    res = await db.execute(stmt)
    return [MessageResponse.model_validate(m) for m in res.scalars().all()]

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    c_res = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.business_id == business.id)
    )
    conv = c_res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Fetch customer
    cust_res = await db.execute(select(Customer).where(Customer.id == conv.customer_id))
    cust = cust_res.scalar_one_or_none()

    msg = Message(
        conversation_id=conv.id,
        sender_type=data.sender_type or MessageSenderType.AGENT.value,
        channel=conv.channel,
        content=data.content,
        media_url=data.media_url,
        media_type=data.media_type,
        is_internal=data.is_internal
    )
    db.add(msg)

    # Update conversation timestamp
    now = datetime.now(timezone.utc)
    conv.last_message_at = now
    if cust:
        cust.last_interaction = now

    # Dispatch to external channel provider if not internal
    if not data.is_internal:
        if conv.channel == "INSTAGRAM":
            ig_provider = MetaInstagramProvider()
            if data.media_url:
                await ig_provider.send_media_message(
                    recipient_id=cust.phone or "mock_recipient",
                    media_url=data.media_url,
                    caption=data.content
                )
            else:
                await ig_provider.send_text_message(
                    recipient_id=cust.phone or "mock_recipient",
                    text=data.content
                )
        elif conv.channel == "WHATSAPP":
            wa_provider = MetaWhatsAppCloudProvider()
            if data.media_url:
                await wa_provider.send_media_message(
                    recipient_id=cust.phone or "919876543210",
                    media_url=data.media_url,
                    caption=data.content
                )
            else:
                await wa_provider.send_text_message(
                    recipient_id=cust.phone or "919876543210",
                    text=data.content
                )

    await db.commit()
    await db.refresh(msg)
    return MessageResponse.model_validate(msg)

@router.post("/{conversation_id}/handoff", response_model=ConversationResponse)
async def update_handoff(
    conversation_id: str,
    data: HumanHandoffRequest,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    c_res = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.business_id == business.id)
    )
    conv = c_res.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv.is_ai_handled = data.is_ai_handled
    conv.status = ConversationStatus.HUMAN_REQUIRED.value if not data.is_ai_handled else ConversationStatus.AI_HANDLING.value
    conv.handoff_reason = data.reason if not data.is_ai_handled else None

    await db.commit()
    await db.refresh(conv)

    cust_res = await db.execute(select(Customer).where(Customer.id == conv.customer_id))
    cust = cust_res.scalar_one_or_none()

    return ConversationResponse(
        id=conv.id,
        business_id=conv.business_id,
        customer_id=conv.customer_id,
        customer_name=cust.name if cust else None,
        customer_phone=cust.phone if cust else None,
        channel=conv.channel,
        status=conv.status,
        is_ai_handled=conv.is_ai_handled,
        handoff_reason=conv.handoff_reason,
        last_message_at=conv.last_message_at,
        created_at=conv.created_at,
        latest_message=None
    )
