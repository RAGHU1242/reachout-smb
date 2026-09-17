# AI Sales Agent Architecture & Safety Rules

## Gemini Flash Model Configuration

ReachOut SMB configures production-grade Google Gemini models optimized for ultra-low latency conversational tool use.

The active model is configurable via:
```env
GEMINI_MODEL=gemini-2.5-flash
```

## Anti-Hallucination Guardrails

The sales agent is **strictly tool-bound**:
1. **Never Invent Prices**: Prices and compare-at prices must come from `search_products` or `get_product`.
2. **Never Fabricate Stock**: If `check_inventory` returns 0, the assistant must state that the item is currently out of stock.
3. **Deterministic Delivery Calculation**: Shipping charges are calculated by `calculate_delivery` using backend locality matrices (e.g. Miyapur ₹50, Kukatpally ₹50).
4. **Authoritative Order State**: An order is only confirmed when `create_order` executes against the database and returns an order number (e.g. `RO-20260917-1001`).

## Multilingual Support

The agent understands and responds naturally in:
- **Telugu** (e.g. *"Anna red saree undha?"* -> *"ఉందండి 😊 మా దగ్గర అందమైన Crimson Kanjeevaram Silk Saree రెడీ స్టాక్ ఉంది! ధర: ₹1,299."*)
- **Hindi** (e.g. *"Banarasi saree dikhao please."* -> *"नमस्ते जी 😊 हमारे पास Royal Emerald Green Banarasi Saree उपलब्ध है।"*)
- **English** (e.g. *"Do you have silk sarees under 1500?"*)
- **Regional Mixed Idioms**: Automatically detects Romanized Telugu ("Hyd lo delivery chesthara?", "Tomorrow kavali").

## Human Handoff Triggers

The agent pauses automation and transfers control to human staff when:
- Customer requests an agent (*"talk to human"*, *"agent please"*, *"manishi kavali"*).
- Negative sentiment, complaint, or dispute keywords appear.
- Manual toggle in the dashboard inbox.
