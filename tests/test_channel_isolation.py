import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.database.session import AsyncSessionLocal
from app.models.models import Business, ChannelAccount, Conversation, Customer

@pytest.mark.asyncio
async def test_multi_tenant_channel_isolation(async_client: AsyncClient):
    """
    Validates that:
    - Business A has Instagram Account IG_A
    - Business B has Instagram Account IG_B
    - Incoming webhook for IG_A routes ONLY to Business A
    - Incoming webhook for IG_B routes ONLY to Business B
    - Conversations and messages never leak across businesses
    """
    import uuid
    uid = uuid.uuid4().hex[:8]
    async with AsyncSessionLocal() as session:
        # Create Business A
        biz_a = Business(
            name=f"Business A Boutique {uid}",
            slug=f"business-a-{uid}",
            location="Hyderabad",
            city="Hyderabad",
            languages=["Telugu", "English"],
            active=True
        )
        # Create Business B
        biz_b = Business(
            name=f"Business B Sarees {uid}",
            slug=f"business-b-{uid}",
            location="Secunderabad",
            city="Secunderabad",
            languages=["Telugu", "English"],
            active=True
        )
        session.add_all([biz_a, biz_b])
        await session.flush()

        # Channel Accounts
        chan_a = ChannelAccount(
            business_id=biz_a.id,
            channel="INSTAGRAM",
            account_id=f"ig_account_alpha_{uid}",
            username="biz_a_insta"
        )
        chan_b = ChannelAccount(
            business_id=biz_b.id,
            channel="INSTAGRAM",
            account_id=f"ig_account_beta_{uid}",
            username="biz_b_insta"
        )
        session.add_all([chan_a, chan_b])
        await session.commit()
        biz_a_id = biz_a.id
        biz_b_id = biz_b.id

    # 1. Simulate incoming Meta Webhook for Business A
    payload_a = {
        "object": "instagram",
        "entry": [
            {
                "id": f"entry_a_{uid}",
                "time": 1773800000,
                "messaging": [
                    {
                        "sender": {"id": f"customer_user_101_{uid}"},
                        "recipient": {"id": f"ig_account_alpha_{uid}"},
                        "message": {
                            "mid": f"m_test_msg_alpha_{uid}",
                            "text": "Hello Business A, red saree undha?"
                        }
                    }
                ]
            }
        ]
    }
    res_a = await async_client.post("/api/v1/webhooks/instagram", json=payload_a)
    assert res_a.status_code == 200

    # 2. Simulate incoming Meta Webhook for Business B
    payload_b = {
        "object": "instagram",
        "entry": [
            {
                "id": f"entry_b_{uid}",
                "time": 1773800001,
                "messaging": [
                    {
                        "sender": {"id": f"customer_user_202_{uid}"},
                        "recipient": {"id": f"ig_account_beta_{uid}"},
                        "message": {
                            "mid": f"m_test_msg_beta_{uid}",
                            "text": "Hello Business B, what are your store timings?"
                        }
                    }
                ]
            }
        ]
    }
    res_b = await async_client.post("/api/v1/webhooks/instagram", json=payload_b)
    assert res_b.status_code == 200

    # 3. Verify in database:
    async with AsyncSessionLocal() as session:
        # Conversations for Business A
        convs_a = await session.execute(
            select(Conversation).where(Conversation.business_id == biz_a_id)
        )
        list_a = convs_a.scalars().all()
        assert len(list_a) == 1

        # Conversations for Business B
        convs_b = await session.execute(
            select(Conversation).where(Conversation.business_id == biz_b_id)
        )
        list_b = convs_b.scalars().all()
        assert len(list_b) == 1

        # Check customer isolation
        cust_a = await session.get(Customer, list_a[0].customer_id)
        cust_b = await session.get(Customer, list_b[0].customer_id)
        assert cust_a.business_id == biz_a_id
        assert cust_b.business_id == biz_b_id
        assert cust_a.phone == f"customer_user_101_{uid}"
        assert cust_b.phone == f"customer_user_202_{uid}"

        # Cross-leak check: Neither conversation contains the other's business_id
        assert list_a[0].business_id != list_b[0].business_id
