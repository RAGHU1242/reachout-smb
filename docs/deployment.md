# Deployment Guide

ReachOut SMB is designed for cloud deployment on Vercel (Frontend) and Supabase / Render / Railway / Fly.io / AWS ECS (FastAPI Backend).

## 1. Frontend Deployment (Vercel)

1. Push your repository to GitHub.
2. In Vercel, click **Add New Project** and select `reachout-smb`.
3. Set **Root Directory** to `frontend`.
4. Add the following Environment Variables in Vercel:
   ```env
   NEXT_PUBLIC_API_URL=https://<YOUR_BACKEND_DOMAIN>
   NEXT_PUBLIC_APP_URL=https://<YOUR_VERCEL_DOMAIN>
   ```
5. Click **Deploy**.

---

## 2. Backend Deployment (Render / Railway / Fly.io / Docker)

A production Dockerfile is provided at `backend/Dockerfile`.

### Required Production Environment Variables:
```env
DATABASE_URL=postgresql+asyncpg://postgres:<PASSWORD>@db.<REF>.supabase.co:5432/postgres
SUPABASE_URL=https://<REF>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<SERVICE_ROLE_KEY>

GEMINI_API_KEY=<AI_STUDIO_KEY>
GEMINI_MODEL=gemini-2.5-flash

META_APP_ID=<APP_ID>
META_APP_SECRET=<APP_SECRET>
META_GRAPH_API_VERSION=v21.0

INSTAGRAM_VERIFY_TOKEN=<SECRET_VERIFY_TOKEN>
WHATSAPP_VERIFY_TOKEN=<SECRET_VERIFY_TOKEN>
WHATSAPP_ACCESS_TOKEN=<SYSTEM_USER_PERMANENT_TOKEN>
WHATSAPP_PHONE_NUMBER_ID=<PHONE_NUMBER_ID>
WHATSAPP_BUSINESS_ACCOUNT_ID=<WABA_ID>

BACKEND_PUBLIC_URL=https://<YOUR_BACKEND_DOMAIN>
JWT_SECRET=<STRONG_64_CHAR_SECRET>

MOCK_AI=false
MOCK_INSTAGRAM=false
MOCK_WHATSAPP=false
MOCK_PAYMENTS=false
```

---

## 3. Meta Webhook URL Configuration

Once the backend is live with HTTPS:
- **Instagram Webhook**: `https://<YOUR_BACKEND_DOMAIN>/api/v1/webhooks/instagram`
- **WhatsApp Webhook**: `https://<YOUR_BACKEND_DOMAIN>/api/v1/webhooks/whatsapp`
- Both respond to GET verification challenges and process inbound messages via POST.
