import hmac
import hashlib
import logging
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.integrations.interfaces import InstagramProvider

logger = logging.getLogger("reachout.instagram")

class MetaInstagramProvider(InstagramProvider):
    def __init__(
        self,
        access_token: Optional[str] = None,
        app_secret: Optional[str] = None,
        api_version: Optional[str] = None
    ):
        self.access_token = access_token
        self.app_secret = app_secret or settings.META_APP_SECRET
        self.api_version = api_version or settings.META_GRAPH_API_VERSION or "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def verify_webhook_signature(self, payload_bytes: bytes, signature_header: Optional[str]) -> bool:
        """
        Verifies the X-Hub-Signature-256 header sent by Meta webhooks.
        """
        if not signature_header or not self.app_secret:
            # If app secret is not configured in dev, pass gracefully in mock mode
            if settings.MOCK_INSTAGRAM:
                return True
            return False

        if not signature_header.startswith("sha256="):
            return False

        expected_sig = signature_header[7:]
        computed_sig = hmac.new(
            self.app_secret.encode("utf-8"),
            msg=payload_bytes,
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed_sig, expected_sig)

    async def send_text_message(self, recipient_id: str, text: str) -> Dict[str, Any]:
        """
        Sends an Instagram Direct message to a customer.
        """
        if settings.MOCK_INSTAGRAM or not self.access_token:
            logger.info(f"[MOCK IG] Sent DM to {recipient_id}: {text}")
            return {"recipient_id": recipient_id, "message_id": f"mock_ig_msg_{hashlib.md5(text.encode()).hexdigest()[:10]}"}

        url = f"{self.base_url}/me/messages"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": text}
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Instagram send text error: {e.response.text}")
                return {"error": e.response.text, "status_code": e.response.status_code}
            except Exception as e:
                logger.error(f"Instagram send unexpected error: {e}")
                return {"error": str(e)}

    async def send_media_message(
        self,
        recipient_id: str,
        media_url: str,
        media_type: str = "image",
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends an image or media attachment directly into Instagram DM.
        """
        if settings.MOCK_INSTAGRAM or not self.access_token:
            logger.info(f"[MOCK IG] Sent media to {recipient_id}: {media_url} (caption: {caption})")
            return {"recipient_id": recipient_id, "message_id": f"mock_ig_media_{recipient_id}"}

        url = f"{self.base_url}/me/messages"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "image",
                    "payload": {
                        "url": media_url,
                        "is_reusable": True
                    }
                }
            }
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                # If caption exists, send follow-up text
                if caption:
                    await self.send_text_message(recipient_id, caption)

                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Instagram send media error: {e.response.text}")
                return {"error": e.response.text, "status_code": e.response.status_code}
            except Exception as e:
                logger.error(f"Instagram send media error: {e}")
                return {"error": str(e)}

    async def get_account_profile(self, access_token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/me?fields=id,name,username,profile_picture_url"
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=headers)
            res.raise_for_status()
            return res.json()
