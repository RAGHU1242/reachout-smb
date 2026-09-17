# ReachOut SMB

**AI Sales & Customer Assistant for WhatsApp and Instagram Businesses**

ReachOut SMB is a multi-tenant SaaS application that enables small and medium businesses (SMBs) in India and globally to sell autonomously across Instagram Direct Messages and WhatsApp with natural multilingual conversational AI powered by Google Gemini Flash, backed by a FastAPI backend, PostgreSQL database, and Next.js 15 App Router dashboard.

---

## Key Features

- **Multilingual AI Sales Agent**: Native support for Telugu, Hindi, and English (including colloquial phrases like *"Anna red saree undha?"*, *"Price entha?"*, *"Hyd lo delivery chesthara?"*).
- **Strict Anti-Hallucination Guardrails**: AI never fabricates prices, discounts, stock availability, or delivery charges. Every recommendation and computation is backed by authoritative backend tools.
- **Unified 3-Column Inbox**: Manage Instagram DMs, WhatsApp conversations, and mock messages in one inbox with real-time media previews and 1-click human takeover.
- **Deterministic Order State Machine**: Strict status transitions (`NEW` &rarr; `CONFIRMED` &rarr; `PROCESSING` &rarr; `SHIPPED` &rarr; `DELIVERED`).
- **Locality-Based Delivery Engine**: Configurable delivery zones (e.g. Miyapur ₹50, Kukatpally ₹50) with automated free delivery thresholds.
- **AI-Assisted Lead Scoring**: Automatically scores incoming customer intent (0–100) and categorizes leads into Hot, Warm, Cold, and Converted.
- **Meta Graph API v21.0+ Architecture**: Production-grade adapters for Instagram Messaging and WhatsApp Cloud API with HMAC SHA-256 signature verification and replay-safe idempotency.
- **Interactive Multi-Channel Simulator (`/dev/simulator`)**: Complete testbed for verifying the full conversational sales funnel offline without Meta credentials.

---

## Quickstart Guide

### 1. Prerequisites

- Python 3.11+
- Node.js 20+

### 2. Backend Setup

```bash
# Set up Python virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows (.venv/bin/activate on Linux/Mac)

# Install dependencies
pip install -r backend/requirements.txt

# Run database migrations
alembic -c alembic.ini upgrade head

# Seed Rani Fashions demo business (20 products, 5 delivery zones, 10 customers, 8 orders)
python scripts/seed_demo_data.py

# Start FastAPI server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at `http://localhost:8000/docs`.

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Dashboard will be live at `http://localhost:3000`.

---

## Demo Business Credentials

- **Email**: `demo@reachoutsmb.com`
- **Password**: `password123`
- **Business**: Rani Fashions (Hyderabad)

Or use the **"Use Demo Account"** button on the `/login` page.

---

## Critical Live Demo Verification

1. Navigate to `http://localhost:3000/dev/simulator`.
2. Click **"Step 1: Telugu Enquiry"**:
   - Customer sends: *"Anna red saree undha? Under 1500 kavali."*
   - AI calls `search_products`, responds in Telugu with the Crimson Kanjeevaram Saree, price (₹1,299), and product image.
3. Click **"Step 2: Delivery Check"**:
   - Customer sends: *"Delivery Miyapur?"*
   - AI calls `calculate_delivery`, returns ₹50 delivery charge.
4. Click **"Step 3: Book Order"**:
   - Customer sends: *"Okay book chesthara. Flat 304, Sri Sai Residency, Miyapur, Hyderabad"*
   - AI calls `create_order`, books the order, decrements inventory, and outputs order number (`RO-...`).
5. Open `/dashboard` or `/orders` to verify the new order!

---

## Running Automated Tests

```bash
.venv\Scripts\activate
pytest tests/ -v
```

All 7 test suites validate:
- Conversational sales agent Telugu & English flow
- Automatic human handoff escalation
- Tenant authorization & data isolation (HTTP 403)
- Locality delivery fee & free delivery threshold
- Instagram webhook challenge
- WhatsApp Cloud API challenge
- Duplicate webhook idempotency

---

## Documentation Directory

- [`docs/architecture.md`](file:///c:/Raghu/AI%20Sales%20&%20Order%20Assistant/docs/architecture.md): System architecture and provider interfaces
- [`docs/setup.md`](file:///c:/Raghu/AI%20Sales%20&%20Order%20Assistant/docs/setup.md): Complete local setup and environment configuration
- [`docs/database.md`](file:///c:/Raghu/AI%20Sales%20&%20Order%20Assistant/docs/database.md): 31-table normalized PostgreSQL schema
- [`docs/ai-agent.md`](file:///c:/Raghu/AI%20Sales%20&%20Order%20Assistant/docs/ai-agent.md): Gemini Flash agent safety rules & tools
- [`docs/instagram.md`](file:///c:/Raghu/AI%20Sales%20&%20Order%20Assistant/docs/instagram.md): Meta Graph API v21.0+ Instagram Messaging guide
- [`docs/whatsapp.md`](file:///c:/Raghu/AI%20Sales%20&%20Order%20Assistant/docs/whatsapp.md): Meta WhatsApp Cloud API guide
- [`docs/deployment.md`](file:///c:/Raghu/AI%20Sales%20&%20Order%20Assistant/docs/deployment.md): Vercel & production backend deployment
- [`docs/security.md`](file:///c:/Raghu/AI%20Sales%20&%20Order%20Assistant/docs/security.md): HMAC verification, tenant isolation, and credential protection
- [`docs/testing.md`](file:///c:/Raghu/AI%20Sales%20&%20Order%20Assistant/docs/testing.md): Automated test coverage
- [`docs/monetization.md`](file:///c:/Raghu/AI%20Sales%20&%20Order%20Assistant/docs/monetization.md): Multi-tenant subscription tiers roadmap
