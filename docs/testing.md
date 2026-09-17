# Automated Testing Suite & Validation

ReachOut SMB includes automated test coverage for core business operations.

## Running Tests

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run full test suite with verbose output
pytest tests/ -v
```

## Test Suites

1. **`tests/test_ai_sales_agent.py`**:
   - Critical live demo conversational flow:
     - Customer sends: *"Anna red saree undha?"*
     - AI tool call `search_products` returns matching Crimson Kanjeevaram Saree with image and ₹1,299 price.
     - Customer sends: *"Delivery Miyapur?"*
     - AI tool call `calculate_delivery` calculates ₹50 fee.
     - Customer confirms order: *"Okay book it. Flat 304, Miyapur, Hyderabad"*.
     - AI tool call `create_order` places confirmed order and updates customer lifetime metrics.
   - Human handoff escalation trigger verification.

2. **`tests/test_auth_tenancy.py`**:
   - User registration and login token generation.
   - Strict multi-tenant access control: User A cannot read Business B data (HTTP 403).

3. **`tests/test_delivery_and_orders.py`**:
   - Locality-based delivery calculation (Miyapur ₹50).
   - Free delivery threshold verification for orders above ₹2,500.
   - Order creation and deterministic status transitions (`CONFIRMED` -> `PROCESSING`).

4. **`tests/test_webhooks_idempotency.py`**:
   - Instagram GET verification challenge (`hub.challenge`).
   - WhatsApp GET verification challenge.
   - Replay attack / duplicate webhook idempotency test.
