import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.models import (
    Business, BusinessMember, BusinessSettings, AISettings, User,
    DeliveryZone, ChannelAccount
)
from app.models.enums import RoleEnum
from app.schemas.schemas import (
    BusinessCreate, BusinessResponse, BusinessUpdate, OnboardingRequest,
    BusinessSettingsSchema, AISettingsSchema, BusinessMemberResponse, BusinessMemberInvite
)
from app.core.dependencies import get_current_user, get_current_business, require_roles

router = APIRouter(prefix="/businesses", tags=["Businesses & Multi-Tenancy"])

def slugify(text: str) -> str:
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

@router.get("", response_model=List[BusinessResponse])
async def list_user_businesses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Business)
        .join(BusinessMember, BusinessMember.business_id == Business.id)
        .where(BusinessMember.user_id == current_user.id)
    )
    result = await db.execute(query)
    return [BusinessResponse.model_validate(b) for b in result.scalars().all()]

@router.post("/onboarding", response_model=BusinessResponse)
async def onboard_business(
    data: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    base_slug = slugify(data.name)
    slug = base_slug
    idx = 1
    while True:
        existing = await db.execute(select(Business).where(Business.slug == slug))
        if not existing.scalar_one_or_none():
            break
        slug = f"{base_slug}-{idx}"
        idx += 1

    business = Business(
        name=data.name,
        slug=slug,
        business_type=data.business_type,
        location=data.location,
        city=data.city,
        currency=data.currency,
        languages=data.languages,
        return_policy=data.return_policy,
        description=data.description,
        active=True
    )
    db.add(business)
    await db.flush()

    # Add owner membership
    member = BusinessMember(
        business_id=business.id,
        user_id=current_user.id,
        role=RoleEnum.OWNER.value
    )
    db.add(member)

    # Initialize business settings
    settings = BusinessSettings(
        business_id=business.id,
        store_timings="Mon-Sat: 10:00 AM - 9:00 PM, Sun: 11:00 AM - 7:00 PM",
        payment_methods=data.payment_methods,
        delivery_regions=data.delivery_regions,
        contact_email=current_user.email
    )
    db.add(settings)

    # Initialize AI settings
    ai_settings = AISettings(
        business_id=business.id,
        enabled=True,
        model_name="gemini-2.5-flash",
        default_language=data.languages[0] if data.languages else "Telugu"
    )
    db.add(ai_settings)

    # Seed default delivery zones for the city
    default_zones = [
        {"locality": "Miyapur", "delivery_fee": 50.0, "pincode": "500049"},
        {"locality": "Kukatpally", "delivery_fee": 50.0, "pincode": "500072"},
        {"locality": "Gachibowli", "delivery_fee": 70.0, "pincode": "500032"},
        {"locality": "Banjara Hills", "delivery_fee": 80.0, "pincode": "500034"},
        {"locality": "Secunderabad", "delivery_fee": 60.0, "pincode": "500003"},
    ]
    for z in default_zones:
        db.add(DeliveryZone(
            business_id=business.id,
            city=data.city,
            locality=z["locality"],
            pincode=z["pincode"],
            delivery_fee=z["delivery_fee"],
            minimum_order=0.0,
            active=True
        ))

    # If Instagram connection checked
    if data.connect_instagram:
        db.add(ChannelAccount(
            business_id=business.id,
            channel="INSTAGRAM",
            account_id="instagram_pro_demo_123",
            username=f"{slug}_official",
            display_name=data.name,
            status="CONNECTED"
        ))

    # If WhatsApp connection checked
    if data.connect_whatsapp:
        db.add(ChannelAccount(
            business_id=business.id,
            channel="WHATSAPP",
            account_id="whatsapp_waba_demo_456",
            username="+919876543210",
            display_name=data.name,
            status="CONNECTED"
        ))

    await db.commit()
    await db.refresh(business)
    return BusinessResponse.model_validate(business)

@router.get("/current", response_model=BusinessResponse)
async def get_current_active_business(
    business: Business = Depends(get_current_business)
):
    return BusinessResponse.model_validate(business)

@router.put("/current", response_model=BusinessResponse)
async def update_current_business(
    data: BusinessUpdate,
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(business, field, val)
    await db.commit()
    await db.refresh(business)
    return BusinessResponse.model_validate(business)

@router.get("/current/settings", response_model=BusinessSettingsSchema)
async def get_settings(
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(BusinessSettings).where(BusinessSettings.business_id == business.id))
    s = res.scalar_one_or_none()
    if not s:
        s = BusinessSettings(business_id=business.id)
        db.add(s)
        await db.commit()
        await db.refresh(s)
    return BusinessSettingsSchema.model_validate(s)

@router.put("/current/settings", response_model=BusinessSettingsSchema)
async def update_settings(
    data: BusinessSettingsSchema,
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(BusinessSettings).where(BusinessSettings.business_id == business.id))
    s = res.scalar_one_or_none()
    if not s:
        s = BusinessSettings(business_id=business.id)
        db.add(s)
    for field, val in data.model_dump().items():
        setattr(s, field, val)
    await db.commit()
    await db.refresh(s)
    return BusinessSettingsSchema.model_validate(s)

@router.get("/current/ai-settings", response_model=AISettingsSchema)
async def get_ai_settings(
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(AISettings).where(AISettings.business_id == business.id))
    s = res.scalar_one_or_none()
    if not s:
        s = AISettings(business_id=business.id)
        db.add(s)
        await db.commit()
        await db.refresh(s)
    return AISettingsSchema.model_validate(s)

@router.put("/current/ai-settings", response_model=AISettingsSchema)
async def update_ai_settings(
    data: AISettingsSchema,
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(AISettings).where(AISettings.business_id == business.id))
    s = res.scalar_one_or_none()
    if not s:
        s = AISettings(business_id=business.id)
        db.add(s)
    for field, val in data.model_dump().items():
        setattr(s, field, val)
    await db.commit()
    await db.refresh(s)
    return AISettingsSchema.model_validate(s)

@router.get("/current/members", response_model=List[BusinessMemberResponse])
async def list_business_members(
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(BusinessMember, User.email, User.full_name)
        .join(User, User.id == BusinessMember.user_id)
        .where(BusinessMember.business_id == business.id)
    )
    res = await db.execute(stmt)
    rows = res.all()
    return [
        BusinessMemberResponse(
            id=m.id,
            business_id=m.business_id,
            user_id=m.user_id,
            email=u_email,
            full_name=u_name,
            role=m.role,
            status="Active",
            created_at=m.created_at
        ) for m, u_email, u_name in rows
    ]

@router.post("/current/members", response_model=BusinessMemberResponse)
async def add_business_member(
    data: BusinessMemberInvite,
    business: Business = Depends(get_current_business),
    _member: BusinessMember = Depends(require_roles([RoleEnum.OWNER, RoleEnum.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    u_res = await db.execute(select(User).where(User.email == data.email))
    user = u_res.scalar_one_or_none()
    if not user:
        from app.core.security import get_password_hash
        user = User(
            email=data.email,
            hashed_password=get_password_hash("ReachOut@2026"),
            full_name=data.full_name,
            is_active=True
        )
        db.add(user)
        await db.flush()

    mem_res = await db.execute(
        select(BusinessMember).where(BusinessMember.business_id == business.id, BusinessMember.user_id == user.id)
    )
    if mem_res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member of this business")

    new_mem = BusinessMember(
        business_id=business.id,
        user_id=user.id,
        role=data.role
    )
    db.add(new_mem)
    await db.commit()
    await db.refresh(new_mem)

    return BusinessMemberResponse(
        id=new_mem.id,
        business_id=new_mem.business_id,
        user_id=new_mem.user_id,
        email=user.email,
        full_name=user.full_name,
        role=new_mem.role,
        status="Active",
        created_at=new_mem.created_at
    )
