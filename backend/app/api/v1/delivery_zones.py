from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.models import DeliveryZone, Business
from app.schemas.schemas import (
    DeliveryZoneCreate, DeliveryZoneResponse,
    DeliveryCalculationRequest, DeliveryCalculationResponse
)
from app.core.dependencies import get_current_business
from app.tools.sales_tools import calculate_delivery as calculate_delivery_tool

router = APIRouter(prefix="/delivery-zones", tags=["Delivery Management"])

@router.get("", response_model=List[DeliveryZoneResponse])
async def list_zones(
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(DeliveryZone).where(DeliveryZone.business_id == business.id).order_by(DeliveryZone.locality.asc())
    )
    return [DeliveryZoneResponse.model_validate(z) for z in res.scalars().all()]

@router.post("", response_model=DeliveryZoneResponse)
async def create_zone(
    data: DeliveryZoneCreate,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    zone = DeliveryZone(
        business_id=business.id,
        city=data.city,
        locality=data.locality,
        pincode=data.pincode,
        delivery_fee=data.delivery_fee,
        minimum_order=data.minimum_order,
        estimated_delivery=data.estimated_delivery,
        active=data.active
    )
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return DeliveryZoneResponse.model_validate(zone)

@router.post("/calculate", response_model=DeliveryCalculationResponse)
async def calculate_delivery_endpoint(
    data: DeliveryCalculationRequest,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    calc = await calculate_delivery_tool(
        db=db,
        business_id=business.id,
        locality=data.locality,
        pincode=data.pincode,
        order_amount=data.subtotal
    )
    return DeliveryCalculationResponse(
        zone_id=calc.get("zone_id"),
        locality=calc.get("locality"),
        delivery_fee=calc["delivery_fee"],
        free_delivery=calc["free_delivery_applied"],
        estimated_delivery=calc["estimated_delivery"],
        total=calc["final_total"]
    )
