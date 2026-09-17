import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.models.models import (
    Product, ProductCategory, Inventory, Business, BusinessSettings,
    Customer, CustomerAddress, Lead, LeadEvent, Order, OrderItem,
    DeliveryZone, FollowUpJob, Conversation, AIToolCall
)
from app.models.enums import (
    OrderStatus, PaymentStatus, LeadStatus, FollowUpStatus, ConversationStatus
)

logger = logging.getLogger("reachout.tools")

async def log_tool_execution(
    db: AsyncSession,
    session_id: Optional[str],
    tool_name: str,
    args: Dict[str, Any],
    result: Dict[str, Any],
    error: Optional[str] = None,
    duration_ms: int = 0
):
    if not session_id:
        return
    try:
        call = AIToolCall(
            session_id=session_id,
            tool_name=tool_name,
            arguments_json=args,
            result_json=result,
            error=error,
            duration_ms=duration_ms
        )
        db.add(call)
        await db.commit()
    except Exception as e:
        logger.warning(f"Could not log AI tool call: {e}")

# -------------------------------------------------------------
# Tool 1: search_products
# -------------------------------------------------------------
async def search_products(
    db: AsyncSession,
    business_id: str,
    query: Optional[str] = None,
    category_slug: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 5
) -> Dict[str, Any]:
    stmt = select(Product).where(
        Product.business_id == business_id,
        Product.active == True
    )

    if query:
        q = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(q),
                Product.description.ilike(q),
                Product.sku.ilike(q),
                Product.color.ilike(q)
            )
        )

    if min_price is not None:
        stmt = stmt.where(Product.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.price <= max_price)

    stmt = stmt.limit(limit)
    res = await db.execute(stmt)
    products = res.scalars().all()

    items = []
    for p in products:
        img_urls = [img.image_url for img in p.images] if p.images else []
        items.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "compare_at_price": p.compare_at_price,
            "stock": p.stock,
            "color": p.color,
            "sku": p.sku,
            "images": img_urls,
            "is_in_stock": p.stock > 0
        })

    return {
        "found": len(items) > 0,
        "count": len(items),
        "products": items
    }

# -------------------------------------------------------------
# Tool 2: get_product
# -------------------------------------------------------------
async def get_product(
    db: AsyncSession,
    business_id: str,
    product_id: str
) -> Dict[str, Any]:
    stmt = select(Product).where(
        Product.id == product_id,
        Product.business_id == business_id
    )
    res = await db.execute(stmt)
    p = res.scalar_one_or_none()
    if not p:
        return {"error": "Product not found"}

    img_urls = [img.image_url for img in p.images] if p.images else []
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "sku": p.sku,
        "stock": p.stock,
        "color": p.color,
        "images": img_urls,
        "is_in_stock": p.stock > 0
    }

# -------------------------------------------------------------
# Tool 3: check_inventory
# -------------------------------------------------------------
async def check_inventory(
    db: AsyncSession,
    business_id: str,
    product_id: str,
    variant_id: Optional[str] = None
) -> Dict[str, Any]:
    stmt = select(Product).where(
        Product.id == product_id,
        Product.business_id == business_id
    )
    res = await db.execute(stmt)
    p = res.scalar_one_or_none()
    if not p:
        return {"error": "Product not found", "available": False, "quantity": 0}

    return {
        "product_id": p.id,
        "product_name": p.name,
        "available": p.stock > 0,
        "stock_quantity": p.stock
    }

# -------------------------------------------------------------
# Tool 4: get_business_information
# -------------------------------------------------------------
async def get_business_information(
    db: AsyncSession,
    business_id: str,
    field: Optional[str] = None
) -> Dict[str, Any]:
    biz_res = await db.execute(select(Business).where(Business.id == business_id))
    biz = biz_res.scalar_one_or_none()
    if not biz:
        return {"error": "Business not found"}

    settings_res = await db.execute(select(BusinessSettings).where(BusinessSettings.business_id == business_id))
    b_settings = settings_res.scalar_one_or_none()

    data = {
        "name": biz.name,
        "business_type": biz.business_type,
        "location": biz.location,
        "city": biz.city,
        "currency": biz.currency,
        "languages": biz.languages,
        "return_policy": biz.return_policy or "7 days return/exchange for defective or incorrect items.",
        "description": biz.description,
        "store_timings": b_settings.store_timings if b_settings else "10:00 AM - 9:00 PM",
        "contact_phone": b_settings.contact_phone if b_settings else None,
        "payment_methods": b_settings.payment_methods if b_settings else ["UPI", "Cash on Delivery"],
        "delivery_regions": b_settings.delivery_regions if b_settings else ["Hyderabad Metro"]
    }

    if field and field in data:
        return {field: data[field]}
    return data

# -------------------------------------------------------------
# Tool 5 & 6: Delivery tools
# -------------------------------------------------------------
async def get_delivery_zone(
    db: AsyncSession,
    business_id: str,
    city: Optional[str] = None,
    locality: Optional[str] = None,
    pincode: Optional[str] = None
) -> Dict[str, Any]:
    stmt = select(DeliveryZone).where(
        DeliveryZone.business_id == business_id,
        DeliveryZone.active == True
    )

    if pincode:
        stmt = stmt.where(DeliveryZone.pincode == pincode.strip())
    elif locality:
        stmt = stmt.where(DeliveryZone.locality.ilike(f"%{locality.strip()}%"))

    res = await db.execute(stmt)
    zone = res.scalar_one_or_none()
    if not zone:
        # fallback default
        return {
            "serviceable": True,
            "locality": locality or "Hyderabad Metro",
            "delivery_fee": 60.0,
            "estimated_delivery": "1-2 days",
            "is_custom_zone": False
        }

    return {
        "serviceable": True,
        "zone_id": zone.id,
        "locality": zone.locality,
        "pincode": zone.pincode,
        "delivery_fee": zone.delivery_fee,
        "minimum_order": zone.minimum_order,
        "estimated_delivery": zone.estimated_delivery,
        "is_custom_zone": True
    }

async def calculate_delivery(
    db: AsyncSession,
    business_id: str,
    pincode: Optional[str] = None,
    locality: Optional[str] = None,
    order_amount: float = 0.0
) -> Dict[str, Any]:
    zone_info = await get_delivery_zone(db, business_id, locality=locality, pincode=pincode)
    fee = zone_info.get("delivery_fee", 50.0)

    # Free delivery on orders above 2500
    free_delivery = order_amount >= 2500.0
    actual_fee = 0.0 if free_delivery else fee
    total = order_amount + actual_fee

    return {
        "locality": zone_info.get("locality"),
        "delivery_fee": actual_fee,
        "original_delivery_fee": fee,
        "free_delivery_applied": free_delivery,
        "order_subtotal": order_amount,
        "estimated_delivery": zone_info.get("estimated_delivery", "1-2 days"),
        "final_total": total
    }

# -------------------------------------------------------------
# Tool 7 & 8: Customer CRM tools
# -------------------------------------------------------------
async def get_customer(
    db: AsyncSession,
    business_id: str,
    customer_id: Optional[str] = None,
    phone: Optional[str] = None
) -> Dict[str, Any]:
    stmt = select(Customer).where(Customer.business_id == business_id)
    if customer_id:
        stmt = stmt.where(Customer.id == customer_id)
    elif phone:
        stmt = stmt.where(Customer.phone == phone)
    else:
        return {"error": "Missing customer identifier"}

    res = await db.execute(stmt)
    c = res.scalar_one_or_none()
    if not c:
        return {"found": False}

    return {
        "found": True,
        "id": c.id,
        "name": c.name,
        "phone": c.phone,
        "email": c.email,
        "preferred_language": c.preferred_language,
        "order_count": c.order_count,
        "total_spending": c.total_spending,
        "tags": c.tags
    }

async def update_customer(
    db: AsyncSession,
    business_id: str,
    customer_id: str,
    preferred_language: Optional[str] = None,
    notes: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    stmt = select(Customer).where(Customer.id == customer_id, Customer.business_id == business_id)
    res = await db.execute(stmt)
    c = res.scalar_one_or_none()
    if not c:
        return {"error": "Customer not found"}

    if preferred_language:
        c.preferred_language = preferred_language
    if notes:
        c.notes = f"{c.notes or ''}\n{notes}".strip()
    if tags:
        c.tags = list(set((c.tags or []) + tags))

    await db.commit()
    await db.refresh(c)
    return {"success": True, "customer_id": c.id, "language": c.preferred_language}

# -------------------------------------------------------------
# Tool 9 & 10: Leads tools
# -------------------------------------------------------------
async def create_lead(
    db: AsyncSession,
    business_id: str,
    customer_id: str,
    conversation_id: Optional[str] = None,
    product_interest: Optional[str] = None,
    budget: Optional[float] = None,
    purchase_intent: str = "HIGH",
    status: str = LeadStatus.HOT.value
) -> Dict[str, Any]:
    score = 80 if purchase_intent == "HIGH" else (60 if purchase_intent == "MEDIUM" else 40)
    lead = Lead(
        business_id=business_id,
        customer_id=customer_id,
        conversation_id=conversation_id,
        product_interest=product_interest,
        budget=budget,
        purchase_intent=purchase_intent,
        score=score,
        status=status,
        notes=f"Auto-generated by AI sales agent for inquiry on {product_interest or 'catalogue'}"
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    # add event
    event = LeadEvent(
        lead_id=lead.id,
        event_type="LEAD_CREATED_BY_AI",
        score_delta=score,
        notes=f"AI Agent identified purchase intent ({purchase_intent})"
    )
    db.add(event)
    await db.commit()

    return {
        "success": True,
        "lead_id": lead.id,
        "score": lead.score,
        "status": lead.status
    }

async def update_lead(
    db: AsyncSession,
    business_id: str,
    lead_id: str,
    score: Optional[int] = None,
    status: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    stmt = select(Lead).where(Lead.id == lead_id, Lead.business_id == business_id)
    res = await db.execute(stmt)
    lead = res.scalar_one_or_none()
    if not lead:
        return {"error": "Lead not found"}

    if score is not None:
        lead.score = score
    if status is not None:
        lead.status = status
    if notes:
        lead.notes = f"{lead.notes or ''}\n{notes}".strip()

    await db.commit()
    return {"success": True, "lead_id": lead.id, "status": lead.status, "score": lead.score}

# -------------------------------------------------------------
# Tool 11, 12, 13: Order tools (Deterministic State Machine)
# -------------------------------------------------------------
async def create_order(
    db: AsyncSession,
    business_id: str,
    customer_id: str,
    items: List[Dict[str, Any]],  # [{"product_id": ..., "quantity": 1}]
    delivery_address: str,
    conversation_id: Optional[str] = None,
    locality: Optional[str] = None,
    pincode: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    # Calculate subtotal strictly from DB prices
    subtotal = 0.0
    order_items_to_create = []

    for it in items:
        p_res = await db.execute(
            select(Product).where(Product.id == it["product_id"], Product.business_id == business_id)
        )
        prod = p_res.scalar_one_or_none()
        if not prod:
            return {"error": f"Product with ID {it['product_id']} not found or does not belong to business."}
        if prod.stock < it.get("quantity", 1):
            return {"error": f"Product '{prod.name}' is out of stock or insufficient quantity (available: {prod.stock})."}

        qty = max(1, int(it.get("quantity", 1)))
        unit_price = float(prod.price)
        item_total = unit_price * qty
        subtotal += item_total

        # decrement stock
        prod.stock -= qty

        order_items_to_create.append({
            "product_id": prod.id,
            "product_name": prod.name,
            "unit_price": unit_price,
            "quantity": qty,
            "total_price": item_total
        })

    # Calculate delivery fee
    delivery_calc = await calculate_delivery(db, business_id, locality=locality, pincode=pincode, order_amount=subtotal)
    delivery_fee = delivery_calc["delivery_fee"]
    total = subtotal + delivery_fee

    import random
    order_num = f"RO-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    order = Order(
        business_id=business_id,
        customer_id=customer_id,
        conversation_id=conversation_id,
        order_number=order_num,
        status=OrderStatus.CONFIRMED.value,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        discount=0.0,
        total=total,
        delivery_address=delivery_address,
        notes=notes,
        payment_status=PaymentStatus.PENDING.value
    )
    db.add(order)
    await db.flush()

    for o_it in order_items_to_create:
        item_obj = OrderItem(
            order_id=order.id,
            product_id=o_it["product_id"],
            product_name=o_it["product_name"],
            unit_price=o_it["unit_price"],
            quantity=o_it["quantity"],
            total_price=o_it["total_price"]
        )
        db.add(item_obj)

    # update customer order count and spending
    cust_res = await db.execute(select(Customer).where(Customer.id == customer_id))
    cust = cust_res.scalar_one_or_none()
    if cust:
        cust.order_count += 1
        cust.total_spending += total

    await db.commit()
    await db.refresh(order)

    return {
        "success": True,
        "order_id": order.id,
        "order_number": order.order_number,
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "total": order.total,
        "status": order.status,
        "payment_status": order.payment_status,
        "estimated_delivery": delivery_calc.get("estimated_delivery")
    }

async def get_order_status(
    db: AsyncSession,
    business_id: str,
    order_id_or_number: str
) -> Dict[str, Any]:
    stmt = select(Order).where(
        Order.business_id == business_id,
        or_(Order.id == order_id_or_number, Order.order_number == order_id_or_number)
    )
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()
    if not order:
        return {"error": "Order not found"}

    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "subtotal": order.subtotal,
        "delivery_fee": order.delivery_fee,
        "total": order.total,
        "payment_status": order.payment_status,
        "delivery_address": order.delivery_address,
        "created_at": order.created_at.isoformat()
    }

# -------------------------------------------------------------
# Tool 14 & 15: Follow-Up automation
# -------------------------------------------------------------
async def schedule_follow_up(
    db: AsyncSession,
    business_id: str,
    customer_id: str,
    scheduled_in_hours: int = 24,
    conversation_id: Optional[str] = None,
    channel: str = "INSTAGRAM",
    message: str = "Hi! We noticed you checked out our sarees. Do you have any questions?",
    reason: str = "Enquiry without order"
) -> Dict[str, Any]:
    scheduled_at = datetime.now(timezone.utc) + timedelta(hours=scheduled_in_hours)
    job = FollowUpJob(
        business_id=business_id,
        customer_id=customer_id,
        conversation_id=conversation_id,
        scheduled_at=scheduled_at,
        channel=channel,
        message=message,
        reason=reason,
        status=FollowUpStatus.SCHEDULED.value
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return {
        "success": True,
        "job_id": job.id,
        "scheduled_at": job.scheduled_at.isoformat()
    }

async def cancel_follow_up(
    db: AsyncSession,
    business_id: str,
    job_id: str
) -> Dict[str, Any]:
    stmt = select(FollowUpJob).where(FollowUpJob.id == job_id, FollowUpJob.business_id == business_id)
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()
    if not job:
        return {"error": "Follow-up job not found"}
    job.status = FollowUpStatus.CANCELLED.value
    await db.commit()
    return {"success": True, "cancelled": True}

# -------------------------------------------------------------
# Tool 16: request_human_handoff
# -------------------------------------------------------------
async def request_human_handoff(
    db: AsyncSession,
    business_id: str,
    conversation_id: str,
    reason: str = "Customer requested human assistant"
) -> Dict[str, Any]:
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.business_id == business_id
    )
    res = await db.execute(stmt)
    conv = res.scalar_one_or_none()
    if not conv:
        return {"error": "Conversation not found"}

    conv.status = ConversationStatus.HUMAN_REQUIRED.value
    conv.is_ai_handled = False
    conv.handoff_reason = reason
    await db.commit()

    return {
        "success": True,
        "conversation_id": conv.id,
        "status": conv.status,
        "is_ai_handled": False,
        "reason": reason
    }
