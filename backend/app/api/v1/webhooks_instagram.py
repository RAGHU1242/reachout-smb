import json
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Request, Response, HTTPException, status, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.core.config import settings
from app.models.models import (
    Business, Customer, Conversation, Message, WebhookEvent, ChannelAccount
)
from app.models.enums import ConversationStatus, MessageSenderType, ChannelEnum, CustomerSource
from app.integrations.instagram_provider import MetaInstagramProvider
from app.agents.sales_agent import SalesAgent

router = APIRouter(prefix="/webhooks/instagram", tags=["Instagram Webhooks"])
logger = logging.getLogger("reachout.webhooks.instagram")

@router.get("")
async def verify_instagram_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """
    Meta Webhook Verification Challenge:
    When configuring the webhook in Meta App Dashboard, Meta sends a GET request.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.INSTAGRAM_VERIFY_TOKEN:
        logger.info("Instagram webhook challenge verified successfully.")
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning("Instagram webhook verification token mismatch.")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch")

@router.post("")
async def handle_instagram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Receives incoming Instagram webhook events (DMs, media, delivery).
    Ensures HMAC verification, idempotency, and feeds the Sales AI Engine.
    """
    body_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    provider = MetaInstagramProvider()
    if not provider.verify_webhook_signature(body_bytes, signature):
        logger.warning("Invalid webhook signature from Meta.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    try:
        data = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed JSON")

    # Meta webhook structure: data["entry"][0]["messaging"][0]
    entries = data.get("entry", [])
    for entry in entries:
        messaging_events = entry.get("messaging", [])
        for event in messaging_events:
            event_id = event.get("message", {}).get("mid") or f"ig_evt_{entry.get('id')}_{event.get('timestamp', '')}"
            if not event_id:
                continue

            # Idempotency check: duplicate events must never re-trigger AI or orders
            existing_event = await db.execute(select(WebhookEvent).where(WebhookEvent.event_id == event_id))
            if existing_event.scalar_one_or_none():
                logger.info(f"Duplicate webhook event {event_id} ignored.")
                continue

            # Record event in DB
            webhook_rec = WebhookEvent(
                event_id=event_id,
                channel=ChannelEnum.INSTAGRAM.value,
                event_type="messages",
                payload_json=event,
                processing_status="PROCESSING"
            )
            db.add(webhook_rec)
            await db.commit()

            # Process inbound message
            sender_id = event.get("sender", {}).get("id")
            recipient_id = event.get("recipient", {}).get("id")
            message_obj = event.get("message", {})
            message_text = message_obj.get("text", "")

            # If it's an echo from our own bot, skip processing
            if message_obj.get("is_echo"):
                webhook_rec.processing_status = "IGNORED_ECHO"
                await db.commit()
                continue

            if not sender_id or not message_text:
                continue

            # Find matching business by ChannelAccount or fallback to primary business
            chan_res = await db.execute(
                select(ChannelAccount).where(
                    ChannelAccount.channel == "INSTAGRAM",
                    ChannelAccount.account_id == recipient_id
                )
            )
            chan = chan_res.scalar_one_or_none()

            if chan:
                business_id = chan.business_id
            else:
                # Find default active business
                biz_res = await db.execute(select(Business).where(Business.active == True).limit(1))
                biz = biz_res.scalar_one_or_none()
                if not biz:
                    continue
                business_id = biz.id

            webhook_rec.business_id = business_id

            # Find or create customer
            cust_res = await db.execute(
                select(Customer).where(
                    Customer.business_id == business_id,
                    Customer.phone == sender_id
                )
            )
            customer = cust_res.scalar_one_or_none()
            if not customer:
                customer = Customer(
                    business_id=business_id,
                    name=f"Instagram User ({sender_id[-4:]})",
                    phone=sender_id,
                    source=CustomerSource.INSTAGRAM.value,
                    preferred_language="Telugu"
                )
                db.add(customer)
                await db.flush()

            # Find or create conversation
            conv_res = await db.execute(
                select(Conversation).where(
                    Conversation.business_id == business_id,
                    Conversation.customer_id == customer.id,
                    Conversation.channel == ChannelEnum.INSTAGRAM.value
                )
            )
            conversation = conv_res.scalar_one_or_none()
            if not conversation:
                conversation = Conversation(
                    business_id=business_id,
                    customer_id=customer.id,
                    channel=ChannelEnum.INSTAGRAM.value,
                    status=ConversationStatus.AI_HANDLING.value,
                    is_ai_handled=True
                )
                db.add(conversation)
                await db.flush()

            # Record customer message
            now = datetime.now(timezone.utc)
            incoming_msg = Message(
                conversation_id=conversation.id,
                sender_type=MessageSenderType.CUSTOMER.value,
                sender_id=sender_id,
                channel=ChannelEnum.INSTAGRAM.value,
                content=message_text,
                created_at=now
            )
            db.add(incoming_msg)
            conversation.last_message_at = now
            customer.last_interaction = now
            await db.commit()

            # If AI handling is active, invoke SalesAgent
            if conversation.is_ai_handled:
                agent = SalesAgent(business_id=business_id, db=db)
                ai_output = await agent.process_customer_message(
                    customer_id=customer.id,
                    conversation_id=conversation.id,
                    message_text=message_text,
                    channel="INSTAGRAM"
                )

                # Send AI message back via Instagram provider
                if ai_output.get("media_url"):
                    await provider.send_media_message(
                        recipient_id=sender_id,
                        media_url=ai_output["media_url"],
                        caption=ai_output.get("reply_text")
                    )
                else:
                    await provider.send_text_message(
                        recipient_id=sender_id,
                        text=ai_output.get("reply_text")
                    )

                # Record AI message in database
                ai_msg = Message(
                    conversation_id=conversation.id,
                    sender_type=MessageSenderType.AI.value,
                    channel=ChannelEnum.INSTAGRAM.value,
                    content=ai_output.get("reply_text", ""),
                    media_url=ai_output.get("media_url"),
                    media_type=ai_output.get("media_type")
                )
                db.add(ai_msg)
                conversation.last_message_at = datetime.now(timezone.utc)
                await db.commit()

            webhook_rec.processing_status = "COMPLETED"
            webhook_rec.processed_at = datetime.now(timezone.utc)
            await db.commit()

    return {"status": "EVENT_RECEIVED"}
