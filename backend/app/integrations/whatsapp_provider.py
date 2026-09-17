import hmac
import hashlib
import logging
import httpx
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.integrations.interfaces import WhatsAppProvider

logger = logging.getLogger("reachout.whatsapp")

class MetaWhatsAppCloudProvider(WhatsAppProvider):
    def __init__(
        self,
        access_token: Optional[str] = None,
        phone_number_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        api_version: Optional[str] = None
    ):
        self.access_token = access_token or settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
        self.app_secret = app_secret or settings.WHATSAPP_APP_SECRET or settings.META_APP_SECRET
        self.api_version = api_version or settings.META_GRAPH_API_VERSION or "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def verify_webhook_signature(self, payload_bytes: bytes, signature_header: Optional[str]) -> bool:
        if not signature_header or not self.app_secret:
            if settings.MOCK_WHATSAPP:
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
        Sends a WhatsApp message via WhatsApp Cloud API.
        """
        clean_recipient = recipient_id.replace("+", "").replace("-", "").replace(" ", "")

        if settings.MOCK_WHATSAPP or not (self.access_token and self.phone_number_id):
            logger.info(f"[MOCK WA] Sent message to {clean_recipient}: {text}")
            return {"messaging_product": "whatsapp", "contacts": [{"input": clean_recipient}], "messages": [{"id": f"wamid.mock_{clean_recipient}"}]}

        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_recipient,
            "type": "text",
            "text": {"preview_url": True, "body": text}
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"WhatsApp send text error: {e.response.text}")
                return {"error": e.response.text, "status_code": e.response.status_code}
            except Exception as e:
                logger.error(f"WhatsApp send error: {e}")
                return {"error": str(e)}

    async def send_media_message(
        self,
        recipient_id: str,
        media_url: str,
        media_type: str = "image",
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        clean_recipient = recipient_id.replace("+", "").replace("-", "").replace(" ", "")

        if settings.MOCK_WHATSAPP or not (self.access_token and self.phone_number_id):
            logger.info(f"[MOCK WA] Sent media to {clean_recipient}: {media_url} (caption: {caption})")
            return {"messaging_product": "whatsapp", "contacts": [{"input": clean_recipient}], "messages": [{"id": f"wamid.mock_media_{clean_recipient}"}]}

        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_recipient,
            "type": "image",
            "image": {"link": media_url}
        }
        if caption:
            payload["image"]["caption"] = caption

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"WhatsApp send media error: {e.response.text}")
                return {"error": e.response.text, "status_code": e.response.status_code}
            except Exception as e:
                logger.error(f"WhatsApp send error: {e}")
                return {"error": str(e)}

    async def send_template_message(
        self,
        recipient_phone: str,
        template_name: str,
        language_code: str = "en",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        clean_phone = recipient_phone.replace("+", "").replace("-", "").replace(" ", "")

        if settings.MOCK_WHATSAPP or not (self.access_token and self.phone_number_id):
            logger.info(f"[MOCK WA] Sent template {template_name} to {clean_phone}")
            return {"messaging_product": "whatsapp", "messages": [{"id": f"wamid.mock_tpl_{clean_phone}"}]}

        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }
        if components:
            payload["template"]["components"] = components

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"WhatsApp template error: {e}")
                return {"error": str(e)}
