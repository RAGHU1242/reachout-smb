import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_delivery_calculation_and_orders(async_client: AsyncClient):
    # 1. Login with demo user
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "demo@reachoutsmb.com", "password": "password123"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get current business
    biz_res = await async_client.get("/api/v1/businesses/current", headers=headers)
    assert biz_res.status_code == 200
    business_id = biz_res.json()["id"]

    # 3. Calculate delivery fee for Miyapur
    deliv_res = await async_client.post(
        "/api/v1/delivery-zones/calculate",
        json={"locality": "Miyapur", "subtotal": 1299.0},
        headers=headers
    )
    assert deliv_res.status_code == 200
    data = deliv_res.json()
    assert data["delivery_fee"] == 50.0
    assert data["total"] == 1349.0

    # 4. Check free delivery threshold (>= 2500)
    free_deliv_res = await async_client.post(
        "/api/v1/delivery-zones/calculate",
        json={"locality": "Miyapur", "subtotal": 2800.0},
        headers=headers
    )
    assert free_deliv_res.status_code == 200
    assert free_deliv_res.json()["free_delivery"] is True
    assert free_deliv_res.json()["delivery_fee"] == 0.0

    # 5. List products to get a product for order creation
    prod_res = await async_client.get("/api/v1/products", headers=headers)
    assert prod_res.status_code == 200
    products = prod_res.json()
    assert len(products) > 0
    test_product = products[0]

    # 6. List customers to get a customer
    cust_res = await async_client.get("/api/v1/customers", headers=headers)
    assert cust_res.status_code == 200
    customers = cust_res.json()
    assert len(customers) > 0
    test_cust = customers[0]

    # 7. Create an order
    order_payload = {
        "customer_id": test_cust["id"],
        "items": [{"product_id": test_product["id"], "quantity": 1}],
        "delivery_address": "Plot 101, Miyapur, Hyderabad",
        "locality": "Miyapur"
    }
    ord_res = await async_client.post("/api/v1/orders", json=order_payload, headers=headers)
    assert ord_res.status_code == 200
    created_order = ord_res.json()
    assert created_order["status"] == "CONFIRMED"
    assert created_order["delivery_fee"] == 50.0

    # 8. Transition order status
    update_res = await async_client.put(
        f"/api/v1/orders/{created_order['id']}/status",
        json={"status": "PROCESSING"},
        headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "PROCESSING"

    # 9. Test invalid transition: Jump from PROCESSING to DELIVERED without SHIPPED -> MUST BE 400 BAD REQUEST
    invalid_res = await async_client.put(
        f"/api/v1/orders/{created_order['id']}/status",
        json={"status": "DELIVERED"},
        headers=headers
    )
    assert invalid_res.status_code == 400
    assert "Invalid order status transition" in invalid_res.json()["detail"]

    # 10. Test valid transition: PROCESSING -> SHIPPED -> DELIVERED
    shipped_res = await async_client.put(
        f"/api/v1/orders/{created_order['id']}/status",
        json={"status": "SHIPPED"},
        headers=headers
    )
    assert shipped_res.status_code == 200
    assert shipped_res.json()["status"] == "SHIPPED"

    delivered_res = await async_client.put(
        f"/api/v1/orders/{created_order['id']}/status",
        json={"status": "DELIVERED"},
        headers=headers
    )
    assert delivered_res.status_code == 200
    assert delivered_res.json()["status"] == "DELIVERED"
    assert delivered_res.json()["payment_status"] == "PAID"
