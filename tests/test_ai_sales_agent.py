import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_critical_conversational_sales_flow(async_client: AsyncClient):
    """
    CRITICAL LIVE DEMO VALIDATION:
    1. Customer sends Instagram DM: 'Anna red saree undha?'
    2. System receives message, understands Telugu, calls search_products tool.
    3. AI returns saree details, price (e.g. ₹1,299), and saree image.
    4. Customer asks: 'Delivery Miyapur?'
    5. AI calls calculate_delivery tool -> returns ₹50 delivery charge.
    6. Customer says: 'Okay book it. Flat 201, Miyapur'
    7. AI calls create_order tool -> Order is placed in database.
    """
    # Step 1: Inquire about red saree in Telugu
    sim_res1 = await async_client.post(
        "/api/v1/simulator/message",
        json={
            "channel": "INSTAGRAM",
            "customer_name": "Deepika Rao",
            "customer_phone": "+919988776655",
            "message": "Anna red saree undha?"
        }
    )
    assert sim_res1.status_code == 200
    out1 = sim_res1.json()
    assert "search_products" in out1["tool_calls_executed"]
    assert len(out1["recommended_products"]) > 0
    assert out1["ai_response"]["media_url"] is not None  # Product image attached
    assert "₹" in out1["ai_response"]["content"]

    # Step 2: Inquire about delivery to Miyapur
    sim_res2 = await async_client.post(
        "/api/v1/simulator/message",
        json={
            "channel": "INSTAGRAM",
            "customer_name": "Deepika Rao",
            "customer_phone": "+919988776655",
            "message": "Delivery Miyapur?"
        }
    )
    assert sim_res2.status_code == 200
    out2 = sim_res2.json()
    assert "calculate_delivery" in out2["tool_calls_executed"]
    assert "50" in out2["ai_response"]["content"]  # ₹50 delivery charge

    # Step 3: Confirm order booking
    sim_res3 = await async_client.post(
        "/api/v1/simulator/message",
        json={
            "channel": "INSTAGRAM",
            "customer_name": "Deepika Rao",
            "customer_phone": "+919988776655",
            "message": "Okay book it. Flat 304, Miyapur, Hyderabad"
        }
    )
    assert sim_res3.status_code == 200
    out3 = sim_res3.json()
    assert "create_order" in out3["tool_calls_executed"]
    assert "RO-" in out3["ai_response"]["content"]  # Order number generated

@pytest.mark.asyncio
async def test_human_handoff_escalation(async_client: AsyncClient):
    """
    Validates automatic human handoff when customer requests agent/complaint.
    """
    sim_res = await async_client.post(
        "/api/v1/simulator/message",
        json={
            "channel": "WHATSAPP",
            "customer_name": "Ramesh Kumar",
            "customer_phone": "+919112233445",
            "message": "I need to talk to a human agent right now"
        }
    )
    assert sim_res.status_code == 200
    out = sim_res.json()
    assert "request_human_handoff" in out["tool_calls_executed"]
