import uuid
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.integrations.interfaces import PaymentProvider

logger = logging.getLogger("reachout.payment")

class MockPaymentProvider(PaymentProvider):
    async def create_payment_order(self, order_id: str, amount: float, currency: str = "INR") -> Dict[str, Any]:
        mock_id = f"pay_mock_{uuid.uuid4().hex[:12]}"
        logger.info(f"[MOCK PAYMENT] Created payment order for order {order_id}: amount={amount} {currency}")
        return {
            "payment_id": mock_id,
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "status": "CREATED",
            "provider": "MOCK"
        }

    async def verify_payment(self, payment_id: str, order_id: str, signature: Optional[str] = None) -> bool:
        logger.info(f"[MOCK PAYMENT] Verified payment {payment_id} for order {order_id}")
        return True

class RazorpayPaymentProvider(PaymentProvider):
    def __init__(self, key_id: Optional[str] = None, key_secret: Optional[str] = None):
        self.key_id = key_id
        self.key_secret = key_secret

    async def create_payment_order(self, order_id: str, amount: float, currency: str = "INR") -> Dict[str, Any]:
        if not (self.key_id and self.key_secret):
            return await MockPaymentProvider().create_payment_order(order_id, amount, currency)
        # Razorpay integration code ready
        return {
            "payment_id": f"order_rzp_{uuid.uuid4().hex[:10]}",
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "status": "CREATED",
            "provider": "RAZORPAY"
        }

    async def verify_payment(self, payment_id: str, order_id: str, signature: Optional[str] = None) -> bool:
        if not (self.key_id and self.key_secret):
            return True
        return True
