# System Architecture: ReachOut SMB

ReachOut SMB is built on a clean provider-based multi-tenant microservices-ready SaaS architecture.

## High-Level Diagram

```
                             [ Customer Ingress ]
                     Instagram DM        WhatsApp Cloud API
                          │                      │
                          ▼                      ▼
                   [ Meta Webhooks ]      [ Meta Webhooks ]
                          │                      │
                          └──────────┬───────────┘
                                     ▼
                      ┌──────────────────────────────┐
                      │    FastAPI API Backend       │
                      │  (HMAC Verify & Idempotency) │
                      └──────────────┬───────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
   [ Conversation Engine ]   [ Order State Machine ]   [ Product & Delivery ]
   - Auto Customer Link      - Deterministic States    - Strict DB Pricing
   - AI Handling Toggle      - Payment Transitions     - Locality Pincodes
           │                         │                         │
           ▼                         └───────────┬─────────────┘
   [ Gemini Flash Agent ]                        │
   - Function Calling Tools                      │
   - Multilingual Engine                         │
   - Zero-Hallucination                          │
           │                                     │
           └──────────────────┬──────────────────┘
                              ▼
                 [ Storage & Database Layer ]
               PostgreSQL (Supabase) + Storage
```

## Provider Interfaces

All external systems interact through abstract contracts defined in `backend/app/integrations/interfaces.py`:
- `AIProvider`: Gemini Flash and Mock AI implementations.
- `MessagingProvider`: Ingress verification, message dispatching, and media sending.
- `InstagramProvider`: Instagram Graph API v21.0+ with `instagram_business_manage_messages`.
- `WhatsAppProvider`: Meta WhatsApp Cloud API with template and media support.
- `PaymentProvider`: MockPaymentProvider and Razorpay ready.
- `StorageProvider`: Supabase Storage S3-compatible asset bucket.

## Multi-Tenancy & Security Model

- **Tenant Scoping**: All operational tables (`products`, `customers`, `conversations`, `orders`, `leads`, `delivery_zones`) require a valid `business_id` foreign key.
- **Header Enforcement**: Backend dependencies (`get_current_business`) enforce user membership and reject any cross-tenant data access with HTTP 403 Forbidden.
- **Zero Hallucination Guarantee**: The AI model is strictly tool-bound. Prices, delivery calculations, and inventory numbers are generated only by verified database function calls.
