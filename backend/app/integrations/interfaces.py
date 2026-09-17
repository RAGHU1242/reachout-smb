from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class AIProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None, tools: Optional[List[Any]] = None) -> Dict[str, Any]:
        pass

class MessagingProvider(ABC):
    @abstractmethod
    async def send_text_message(self, recipient_id: str, text: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def send_media_message(self, recipient_id: str, media_url: str, media_type: str, caption: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload_bytes: bytes, signature_header: Optional[str]) -> bool:
        pass

class InstagramProvider(MessagingProvider):
    @abstractmethod
    async def get_account_profile(self, access_token: str) -> Dict[str, Any]:
        pass

class WhatsAppProvider(MessagingProvider):
    @abstractmethod
    async def send_template_message(self, recipient_phone: str, template_name: str, language_code: str, components: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        pass

class PaymentProvider(ABC):
    @abstractmethod
    async def create_payment_order(self, order_id: str, amount: float, currency: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def verify_payment(self, payment_id: str, order_id: str, signature: Optional[str]) -> bool:
        pass

class StorageProvider(ABC):
    @abstractmethod
    async def upload_file(self, file_bytes: bytes, destination_path: str, content_type: str) -> str:
        """Returns public or signed URL"""
        pass

class NotificationProvider(ABC):
    @abstractmethod
    async def send_notification(self, title: str, message: str, recipient: str) -> bool:
        pass
