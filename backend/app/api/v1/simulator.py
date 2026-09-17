from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.models import Business, Customer, Conversation, Message
from app.models.enums import ConversationStatus, MessageSenderType, ChannelEnum, CustomerSource
from app.schemas.schemas import (
    SimulatorMessageRequest, SimulatorMessageResponse, MessageResponse, ProductResponse
)
from app.agents.sales_agent import SalesAgent

router = APIRouter(prefix="/simulator", tags=["Developer Simulator"])

@router.post("/message", response_model=SimulatorMessageResponse)
async def simulate_message(
    data: SimulatorMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    # Determine business
    if data.business_id:
        biz_res = await db.execute(select(Business).where(Business.id == data.business_id))
        business = biz_res.scalar_one_or_none()
    else:
        biz_res = await db.execute(select(Business).where(Business.active == True).limit(1))
        business = biz_res.scalar_one_or_none()

    if not business:
        raise HTTPException(status_code=404, detail="No active business found. Please complete onboarding first.")

    channel = data.channel.upper()
    if channel not in ["INSTAGRAM", "WHATSAPP"]:
        channel = "INSTAGRAM"

    # Find or create customer
    phone = data.customer_phone or "+919876543210"
    cust_res = await db.execute(
        select(Customer).where(Customer.business_id == business.id, Customer.phone == phone)
    )
    customer = cust_res.scalar_one_or_none()
    if not customer:
        customer = Customer(
            business_id=business.id,
            name=data.customer_name,
            phone=phone,
            source=channel,
            preferred_language="Telugu"
        )
        db.add(customer)
        await db.flush()

    # Find or create conversation
    conv_res = await db.execute(
        select(Conversation).where(
            Conversation.business_id == business.id,
            Conversation.customer_id == customer.id,
            Conversation.channel == channel
        )
    )
    conv = conv_res.scalar_one_or_none()
    if not conv:
        conv = Conversation(
            business_id=business.id,
            customer_id=customer.id,
            channel=channel,
            status=ConversationStatus.AI_HANDLING.value,
            is_ai_handled=True
        )
        db.add(conv)
        await db.flush()

    # Record customer message
    now = datetime.now(timezone.utc)
    in_msg = Message(
        conversation_id=conv.id,
        sender_type=MessageSenderType.CUSTOMER.value,
        sender_id=phone,
        channel=channel,
        content=data.message,
        created_at=now
    )
    db.add(in_msg)
    conv.last_message_at = now
    customer.last_interaction = now
    await db.commit()
    await db.refresh(in_msg)

    # Invoke SalesAgent
    agent = SalesAgent(business_id=business.id, db=db)
    ai_output = await agent.process_customer_message(
        customer_id=customer.id,
        conversation_id=conv.id,
        message_text=data.message,
        channel=channel
    )

    # Record AI message
    ai_msg = Message(
        conversation_id=conv.id,
        sender_type=MessageSenderType.AI.value,
        channel=channel,
        content=ai_output.get("reply_text", ""),
        media_url=ai_output.get("media_url"),
        media_type=ai_output.get("media_type"),
        created_at=datetime.now(timezone.utc)
    )
    db.add(ai_msg)
    conv.last_message_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(ai_msg)

    recommended = ai_output.get("recommended_products", [])

    return SimulatorMessageResponse(
        conversation_id=conv.id,
        customer_id=customer.id,
        incoming_message=MessageResponse.model_validate(in_msg),
        ai_response=MessageResponse.model_validate(ai_msg),
        detected_intent="Product Discovery / Order",
        recommended_products=recommended,
        tool_calls_executed=ai_output.get("tool_calls", [])
    )
