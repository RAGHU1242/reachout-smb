# Database Schema Documentation

ReachOut SMB employs a PostgreSQL normalized relational database with Alembic migration versioning.

## Tables Overview

1. **`users`**: System user profiles with email and bcrypt password hashes.
2. **`businesses`**: Tenant business records (name, slug, currency, languages, location).
3. **`business_members`**: Tenancy mappings linking users to businesses with roles (`OWNER`, `ADMIN`, `STAFF`, `VIEWER`).
4. **`business_settings`**: Store hours, contact details, delivery regions, payment methods.
5. **`ai_settings`**: Configured AI model name, default language, escalation keywords.
6. **`product_categories`**: Product taxonomies (e.g. Silk Sarees, Handloom, Party Wear).
7. **`products`**: Catalogue items with pricing, compare-at pricing, SKU, stock quantity, color, size.
8. **`product_images`**: High-resolution image URLs, primary image flag, sort ordering.
9. **`inventory`**: Stock level ledger and low-stock warning thresholds.
10. **`customers`**: Multi-channel customer CRM with language preference and lifetime spending.
11. **`customer_addresses`**: Physical shipping addresses with locality, city, and pincode.
12. **`conversations`**: Unified channel threads with state machine and AI vs Human handoff flag.
13. **`messages`**: Multi-channel message records with text, media URL, sender type, and internal notes.
14. **`leads`**: AI-qualified sales opportunities with dynamic scores (0-100) and status pipeline.
15. **`lead_events`**: Timeline of intent events and score adjustments.
16. **`delivery_zones`**: Locality-based shipping fee matrices (e.g. Miyapur ₹50, Kukatpally ₹50).
17. **`orders`**: Customer orders with subtotal, delivery fee, total, address, and status.
18. **`order_items`**: Order line items capturing snapshot unit prices.
19. **`payments`**: Payment transactions and status (`PENDING`, `PAID`, `REFUNDED`).
20. **`follow_up_jobs`**: Scheduled re-engagement triggers for customer follow-up.
21. **`knowledge_documents`**: Business policies, FAQs, and custom prompt guidelines.
22. **`channel_accounts`**: Connected Instagram Professional and WhatsApp Cloud API accounts.
23. **`webhook_events`**: Idempotency ledger tracking received Meta events to prevent duplicate processing.
