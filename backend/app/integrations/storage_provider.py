import os
import uuid
import logging
import httpx
from typing import Optional
from app.core.config import settings
from app.integrations.interfaces import StorageProvider

logger = logging.getLogger("reachout.storage")

class SupabaseStorageProvider(StorageProvider):
    def __init__(self, supabase_url: Optional[str] = None, service_role_key: Optional[str] = None, bucket: str = "product-images"):
        self.supabase_url = supabase_url or settings.SUPABASE_URL
        self.service_role_key = service_role_key or settings.SUPABASE_SERVICE_ROLE_KEY
        self.bucket = bucket

    async def upload_file(self, file_bytes: bytes, destination_path: str, content_type: str = "image/jpeg") -> str:
        if not self.supabase_url or "mock" in self.supabase_url:
            # Fallback for dev / offline demo
            return f"https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80"

        url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{destination_path}"
        headers = {
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": content_type
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                res = await client.post(url, content=file_bytes, headers=headers)
                res.raise_for_status()
                # Return public URL
                return f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{destination_path}"
            except Exception as e:
                logger.error(f"Supabase storage upload error: {e}")
                return f"https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=800&q=80"
