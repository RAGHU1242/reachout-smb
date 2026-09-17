import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_instagram_webhook_challenge(async_client: AsyncClient):
    res = await async_client.get(
        "/api/v1/webhooks/instagram",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "11582012",
            "hub.verify_token": "reachout_instagram_verify_token_2026"
        }
    )
    assert res.status_code == 200
    assert res.text == "11582012"

@pytest.mark.asyncio
async def test_whatsapp_webhook_challenge(async_client: AsyncClient):
    res = await async_client.get(
        "/api/v1/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "99887766",
            "hub.verify_token": "reachout_whatsapp_verify_token_2026"
        }
    )
    assert res.status_code == 200
    assert res.text == "99887766"

@pytest.mark.asyncio
async def test_webhook_idempotency(async_client: AsyncClient):
    event_payload = {
        "object": "instagram",
        "entry": [
            {
                "id": "17841400000000000",
                "time": 1720000000,
                "messaging": [
                    {
                        "sender": {"id": "ig_user_12345"},
                        "recipient": {"id": "17841400000000000"},
                        "timestamp": 1720000000,
                        "message": {
                            "mid": "mid.1720000000_unique_test_mid_001",
                            "text": "Hello there!"
                        }
                    }
                ]
            }
        ]
    }

    # First delivery
    r1 = await async_client.post("/api/v1/webhooks/instagram", json=event_payload)
    assert r1.status_code == 200

    # Duplicate delivery with the same mid
    r2 = await async_client.post("/api/v1/webhooks/instagram", json=event_payload)
    assert r2.status_code == 200
