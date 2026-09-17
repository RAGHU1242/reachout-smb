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
from app.integrations.whatsapp_provider import MetaWhatsAppCloudProvider
from app.agents.sales_agent import SalesAgent

router = APIRouter(prefix="/webhooks/whatsapp", tags=["WhatsApp Webhooks"])
logger = logging.getLogger("reachout.webhooks.whatsapp")

@router.get("")
async def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook challenge verified successfully.")
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning("WhatsApp webhook verification token mismatch.")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch")

@router.post("")
async def handle_whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    body_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    provider = MetaWhatsAppCloudProvider()
    if not provider.verify_webhook_signature(body_bytes, signature):
        logger.warning("Invalid WhatsApp webhook signature.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    try:
        data = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed JSON")

    entries = data.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            val = change.get("value", {})
            messages = val.get("messages", [])
            contacts = val.get("contacts", [])
            contact_name = contacts[0].get("profile", {}).get("name") if contacts else None

            for msg_item in messages:
                event_id = msg_item.get("id")
                if not event_id:
                    continue

                # Idempotency
                existing_event = await db.execute(select(WebhookEvent).where(WebhookEvent.event_id == event_id))
                if existing_event.scalar_one_or_none():
                    logger.info(f"Duplicate WhatsApp event {event_id} ignored.")
                    continue

                webhook_rec = WebhookEvent(
                    event_id=event_id,
                    channel=ChannelEnum.WHATSAPP.value,
                    event_type="messages",
                    payload_json=msg_item,
                    processing_status="PROCESSING"
                )
                db.add(webhook_rec)
                await db.commit()

                sender_phone = msg_item.get("from")
                msg_type = msg_item.get("type")
                message_text = ""
                if msg_type == "text":
                    message_text = msg_item.get("text", {}).get("body", "")
                elif msg_type == "button":
                    message_text = msg_item.get("button", {}).get("text", "")
                elif msg_type == "interactive":
                    message_text = msg_item.get("interactive", {}).get("button_reply", {}).get("title", "")

                if not sender_phone or not message_text:
                    continue

                # Get business
                phone_num_id = val.get("metadata", {}).get("phone_number_id")
                chan_res = await db.execute(
                    select(ChannelAccount).where(
                        ChannelAccount.channel == "WHATSAPP",
                        ChannelAccount.account_id == phone_num_id
                    )
                )
                chan = chan_res.scalar_one_or_none()
                if chan:
                    business_id = chan.business_id
                else:
                    biz_res = await db.execute(select(Business).where(Business.active == True).limit(1))
                    biz = biz_res.scalar_one_or_none()
                    if not biz:
                        continue
                    business_id = biz.id

                webhook_rec.business_id = business_id

                # Find/create customer
                formatted_phone = f"+{sender_phone}" if not sender_phone.startswith("+") else sender_phone
                cust_res = await db.execute(
                    select(Customer).where(
                        Customer.business_id == business_id,
                        Customer.phone == formatted_phone
                    )
                )
                customer = cust_res.scalar_one_or_none()
                if not customer:
                    customer = Customer(
                        business_id=business_id,
                        name=contact_name or f"WhatsApp Customer ({sender_phone[-4:]})",
                        phone=formatted_phone,
                        source=CustomerSource.WHATSAPP.value,
                        preferred_language="Telugu"
                    )
                    db.add(customer)
                    await db.flush()

                # Find/create conversation
                conv_res = await db.execute(
                    select(Conversation).where(
                        Conversation.business_id == business_id,
                        Conversation.customer_id == customer.id,
                        Conversation.channel == ChannelEnum.WHATSAPP.value
                    )
                )
                conversation = conv_res.scalar_one_or_none()
                if not conversation:
                    conversation = Conversation(
                        business_id=business_id,
                        customer_id=customer.id,
                        channel=ChannelEnum.WHATSAPP.value,
                        status=ConversationStatus.AI_HANDLING.value,
                        is_ai_handled=True
                    )
                    db.add(conversation)
                    await db.flush()

                now = datetime.now(timezone.utc)
                in_msg = Message(
                    conversation_id=conversation.id,
                    sender_type=MessageSenderType.CUSTOMER.value,
                    sender_id=formatted_phone,
                    channel=ChannelEnum.WHATSAPP.value,
                    content=message_text,
                    created_at=now
                )
                db.add(in_msg)
                conversation.last_message_at = now
                customer.last_interaction = now
                await db.commit()

                # Run AI agent
                if conversation.is_ai_handled:
                    agent = SalesAgent(business_id=business_id, db=db)
                    ai_output = await agent.process_customer_message(
                        customer_id=customer.id,
                        conversation_id=conversation.id,
                        message_text=message_text,
                        channel="WHATSAPP"
                    )

                    if ai_output.get("media_url"):
                        await provider.send_media_message(
                            recipient_id=sender_phone,
                            media_url=ai_output["media_url"],
                            caption=ai_output.get("reply_text")
                        )
                    else:
                        await provider.send_text_message(
                            recipient_id=sender_phone,
                            text=ai_output.get("reply_text")
                        )

                    ai_msg = Message(
                        conversation_id=conversation.id,
                        sender_type=MessageSenderType.AI.value,
                        channel=ChannelEnum.WHATSAPP.value,
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
