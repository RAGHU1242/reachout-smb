# Security Architecture & Best Practices

## Core Security Controls

1. **Strict Multi-Tenant Isolation**:
   - Every database query is scoped to `business_id`.
   - Cross-tenant data tampering is rejected at the API dependency layer (`get_current_business`) with HTTP 403 Forbidden.

2. **Secret Separation**:
   - Backend secrets (`GEMINI_API_KEY`, `META_APP_SECRET`, `WHATSAPP_ACCESS_TOKEN`, `SUPABASE_SERVICE_ROLE_KEY`) are stored exclusively on the server side and never sent to frontend bundles or exposed via `NEXT_PUBLIC_` variables.

3. **Webhook Verification & Replay Protection**:
   - Meta `X-Hub-Signature-256` HMAC-SHA256 headers are validated on all incoming webhook payloads using the Meta App Secret.
   - Idempotency is enforced using `webhook_events`: duplicate message IDs (`mid` / `wamid`) are discarded immediately without re-triggering AI tools or creating duplicate orders.

4. **Authentication & Passwords**:
   - Passwords are encrypted with standard bcrypt salting.
   - Sessions are managed with stateless, cryptographically signed HS256 JWT tokens.

5. **No Hallucinated Operations**:
   - Financial figures, product inventory, order placement, and delivery fee calculations are completely isolated from LLM output generation and strictly handled by deterministic backend code.
