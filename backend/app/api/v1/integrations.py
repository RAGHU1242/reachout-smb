from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.models import ChannelAccount, Business, BusinessMember
from app.models.enums import RoleEnum
from app.core.dependencies import get_current_business, require_roles
from app.core.config import settings

router = APIRouter(prefix="/integrations", tags=["Channel Integrations"])

@router.get("/status")
async def get_integrations_status(
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(ChannelAccount).where(ChannelAccount.business_id == business.id)
    )
    accounts = res.scalars().all()

    ig_acc = next((a for a in accounts if a.channel == "INSTAGRAM"), None)
    wa_acc = next((a for a in accounts if a.channel == "WHATSAPP"), None)

    return {
        "instagram": {
            "connected": ig_acc is not None and ig_acc.status == "CONNECTED",
            "account_id": ig_acc.account_id if ig_acc else None,
            "username": ig_acc.username if ig_acc else None,
            "display_name": ig_acc.display_name if ig_acc else None,
            "status": ig_acc.status if ig_acc else "DISCONNECTED",
            "last_webhook_at": ig_acc.last_webhook_at if ig_acc else None,
            "webhook_url": f"{settings.BACKEND_PUBLIC_URL}/api/v1/webhooks/instagram",
            "verify_token": settings.INSTAGRAM_VERIFY_TOKEN
        },
        "whatsapp": {
            "connected": wa_acc is not None and wa_acc.status == "CONNECTED",
            "phone_number_id": wa_acc.account_id if wa_acc else (settings.WHATSAPP_PHONE_NUMBER_ID or None),
            "username": wa_acc.username if wa_acc else None,
            "display_name": wa_acc.display_name if wa_acc else None,
            "status": wa_acc.status if wa_acc else "DISCONNECTED",
            "last_webhook_at": wa_acc.last_webhook_at if wa_acc else None,
            "webhook_url": f"{settings.BACKEND_PUBLIC_URL}/api/v1/webhooks/whatsapp",
            "verify_token": settings.WHATSAPP_VERIFY_TOKEN
        },
        "mock_mode": {
            "mock_ai": settings.MOCK_AI,
            "mock_instagram": settings.MOCK_INSTAGRAM,
            "mock_whatsapp": settings.MOCK_WHATSAPP,
            "mock_payments": settings.MOCK_PAYMENTS
        }
    }

@router.post("/instagram/connect")
async def connect_instagram(
    data: Dict[str, Any],
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    username = data.get("username", f"{business.slug}_official")
    acc_id = data.get("account_id", f"ig_{business.id[:8]}")

    stmt = select(ChannelAccount).where(
        ChannelAccount.business_id == business.id,
        ChannelAccount.channel == "INSTAGRAM"
    )
    res = await db.execute(stmt)
    acc = res.scalar_one_or_none()
    if not acc:
        acc = ChannelAccount(
            business_id=business.id,
            channel="INSTAGRAM",
            account_id=acc_id,
            username=username,
            display_name=business.name,
            status="CONNECTED",
            last_webhook_at=datetime.now(timezone.utc)
        )
        db.add(acc)
    else:
        acc.status = "CONNECTED"
        acc.username = username
        acc.account_id = acc_id
        acc.last_webhook_at = datetime.now(timezone.utc)

    await db.commit()
    return {"success": True, "channel": "INSTAGRAM", "status": "CONNECTED", "username": username}

@router.post("/whatsapp/connect")
async def connect_whatsapp(
    data: Dict[str, Any],
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    phone_number = data.get("phone_number", "+919876543210")
    phone_id = data.get("phone_number_id", f"wa_phone_{business.id[:8]}")

    stmt = select(ChannelAccount).where(
        ChannelAccount.business_id == business.id,
        ChannelAccount.channel == "WHATSAPP"
    )
    res = await db.execute(stmt)
    acc = res.scalar_one_or_none()
    if not acc:
        acc = ChannelAccount(
            business_id=business.id,
            channel="WHATSAPP",
            account_id=phone_id,
            username=phone_number,
            display_name=business.name,
            status="CONNECTED",
            last_webhook_at=datetime.now(timezone.utc)
        )
        db.add(acc)
    else:
        acc.status = "CONNECTED"
        acc.username = phone_number
        acc.account_id = phone_id
        acc.last_webhook_at = datetime.now(timezone.utc)

    await db.commit()
    return {"success": True, "channel": "WHATSAPP", "status": "CONNECTED", "phone_number": phone_number}

@router.post("/{channel}/disconnect")
async def disconnect_channel(
    channel: str,
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    channel_upper = channel.upper()
    stmt = select(ChannelAccount).where(
        ChannelAccount.business_id == business.id,
        ChannelAccount.channel == channel_upper
    )
    res = await db.execute(stmt)
    acc = res.scalar_one_or_none()
    if acc:
        acc.status = "DISCONNECTED"
        await db.commit()
    return {"success": True, "channel": channel_upper, "status": "DISCONNECTED"}
