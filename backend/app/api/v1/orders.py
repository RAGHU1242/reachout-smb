from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.models.models import Order, OrderItem, Customer, Product, Business, BusinessMember
from app.models.enums import OrderStatus, PaymentStatus
from app.schemas.schemas import OrderCreate, OrderResponse, OrderItemResponse, OrderStatusUpdate
from app.core.dependencies import get_current_business
from app.tools.sales_tools import create_order as create_order_tool

router = APIRouter(prefix="/orders", tags=["Orders & Checkout"])

VALID_TRANSITIONS = {
    OrderStatus.NEW.value: [OrderStatus.ITEMS_SELECTED.value, OrderStatus.ADDRESS_REQUIRED.value, OrderStatus.CANCELLED.value],
    OrderStatus.ITEMS_SELECTED.value: [OrderStatus.ADDRESS_REQUIRED.value, OrderStatus.ADDRESS_CONFIRMED.value, OrderStatus.CANCELLED.value],
    OrderStatus.ADDRESS_REQUIRED.value: [OrderStatus.ADDRESS_CONFIRMED.value, OrderStatus.CANCELLED.value],
    OrderStatus.ADDRESS_CONFIRMED.value: [OrderStatus.PAYMENT_PENDING.value, OrderStatus.CONFIRMED.value, OrderStatus.CANCELLED.value],
    OrderStatus.PAYMENT_PENDING.value: [OrderStatus.PAYMENT_CONFIRMED.value, OrderStatus.CONFIRMED.value, OrderStatus.CANCELLED.value],
    OrderStatus.PAYMENT_CONFIRMED.value: [OrderStatus.CONFIRMED.value, OrderStatus.CANCELLED.value],
    OrderStatus.CONFIRMED.value: [OrderStatus.PROCESSING.value, OrderStatus.CANCELLED.value],
    OrderStatus.PROCESSING.value: [OrderStatus.SHIPPED.value, OrderStatus.CANCELLED.value],
    OrderStatus.SHIPPED.value: [OrderStatus.DELIVERED.value, OrderStatus.REFUNDED.value],
    OrderStatus.DELIVERED.value: [OrderStatus.REFUNDED.value],
    OrderStatus.CANCELLED.value: [],
    OrderStatus.REFUNDED.value: []
}

@router.get("", response_model=List[OrderResponse])
async def list_orders(
    status_filter: Optional[str] = None,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Order, Customer.name)
        .join(Customer, Customer.id == Order.customer_id)
        .where(Order.business_id == business.id)
    )
    if status_filter:
        stmt = stmt.where(Order.status == status_filter)
    stmt = stmt.order_by(Order.created_at.desc())
    res = await db.execute(stmt)
    rows = res.all()

    orders_out = []
    for order, cust_name in rows:
        # fetch items
        items_res = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
        items = items_res.scalars().all()
        order_dict = {
            "id": order.id,
            "business_id": order.business_id,
            "customer_id": order.customer_id,
            "customer_name": cust_name,
            "order_number": order.order_number,
            "status": order.status,
            "subtotal": order.subtotal,
            "delivery_fee": order.delivery_fee,
            "discount": order.discount,
            "total": order.total,
            "delivery_address": order.delivery_address,
            "payment_status": order.payment_status,
            "created_at": order.created_at,
            "items": [OrderItemResponse.model_validate(it) for it in items]
        }
        orders_out.append(OrderResponse(**order_dict))
    return orders_out

@router.post("", response_model=OrderResponse)
async def create_order_endpoint(
    data: OrderCreate,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    items_input = [{"product_id": it.product_id, "quantity": it.quantity} for it in data.items]
    res = await create_order_tool(
        db=db,
        business_id=business.id,
        customer_id=data.customer_id,
        conversation_id=data.conversation_id,
        items=items_input,
        delivery_address=data.delivery_address,
        locality=data.locality,
        pincode=data.pincode,
        notes=data.notes
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error", "Failed to create order"))

    order_id = res["order_id"]
    return await get_order_endpoint(order_id, business, db)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(
    order_id: str,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Order, Customer.name)
        .join(Customer, Customer.id == Order.customer_id)
        .where(Order.id == order_id, Order.business_id == business.id)
    )
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")

    order, cust_name = row
    items_res = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
    items = items_res.scalars().all()

    return OrderResponse(
        id=order.id,
        business_id=order.business_id,
        customer_id=order.customer_id,
        customer_name=cust_name,
        order_number=order.order_number,
        status=order.status,
        subtotal=order.subtotal,
        delivery_fee=order.delivery_fee,
        discount=order.discount,
        total=order.total,
        delivery_address=order.delivery_address,
        payment_status=order.payment_status,
        created_at=order.created_at,
        items=[OrderItemResponse.model_validate(it) for it in items]
    )

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    data: OrderStatusUpdate,
    business: Business = Depends(get_current_business),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Order).where(Order.id == order_id, Order.business_id == business.id)
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    new_status = data.status.upper()
    valid_next = VALID_TRANSITIONS.get(order.status, [])
    if new_status not in valid_next:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order status transition from '{order.status}' to '{new_status}'. Allowed transitions: {valid_next}"
        )

    if new_status == OrderStatus.PAYMENT_CONFIRMED.value:
        pay_res = await db.execute(select(Payment).where(Payment.order_id == order.id, Payment.status == PaymentStatus.PAID.value))
        payment = pay_res.scalar_one_or_none()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transition to PAYMENT_CONFIRMED without confirmed payment record."
            )
        order.payment_status = PaymentStatus.PAID.value

    order.status = new_status
    if new_status == OrderStatus.DELIVERED.value:
        order.payment_status = PaymentStatus.PAID.value

    await db.commit()
    await db.refresh(order)
    return await get_order_endpoint(order_id, business, db)
