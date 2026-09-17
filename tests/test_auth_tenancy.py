import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_and_tenant_isolation(async_client: AsyncClient):
    # 1. Register User 1
    u1_payload = {
        "email": "user1@example.com",
        "password": "Password123!",
        "full_name": "User One"
    }
    r1 = await async_client.post("/api/v1/auth/register", json=u1_payload)
    if r1.status_code == 400:
        # Already registered
        r1 = await async_client.post("/api/v1/auth/login", json={"email": "user1@example.com", "password": "Password123!"})
    assert r1.status_code == 200
    token1 = r1.json()["access_token"]

    # 2. Register User 2
    u2_payload = {
        "email": "user2@example.com",
        "password": "Password123!",
        "full_name": "User Two"
    }
    r2 = await async_client.post("/api/v1/auth/register", json=u2_payload)
    if r2.status_code == 400:
        r2 = await async_client.post("/api/v1/auth/login", json={"email": "user2@example.com", "password": "Password123!"})
    assert r2.status_code == 200
    token2 = r2.json()["access_token"]

    # 3. User 1 onboards Business A
    biz_payload = {
        "name": "User One Boutique",
        "business_type": "Fashion",
        "location": "Hyderabad",
        "city": "Hyderabad",
        "languages": ["Telugu", "English"],
        "currency": "INR",
        "delivery_regions": ["Hyderabad"],
        "payment_methods": ["UPI"]
    }
    b1_res = await async_client.post(
        "/api/v1/businesses/onboarding",
        json=biz_payload,
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert b1_res.status_code == 200
    biz1_id = b1_res.json()["id"]

    # 4. User 2 attempts to access Business A data -> MUST BE 403 FORBIDDEN
    forbidden_res = await async_client.get(
        "/api/v1/businesses/current",
        headers={
            "Authorization": f"Bearer {token2}",
            "X-Business-Id": biz1_id
        }
    )
    assert forbidden_res.status_code == 403
