"""enable_rls_and_tenant_security

Revision ID: 6f1a89c02d3e
Revises: 5dc6093a8857
Create Date: 2026-09-18 10:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '6f1a89c02d3e'
down_revision: Union[str, Sequence[str], None] = '5dc6093a8857'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PUBLIC_TABLES = [
    "users", "businesses", "business_members", "business_settings", "ai_settings",
    "product_categories", "products", "product_variants", "product_images", "inventory",
    "customers", "customer_addresses", "conversations", "conversation_participants", "messages",
    "leads", "lead_events", "delivery_zones", "orders", "order_items", "payments",
    "follow_up_jobs", "knowledge_documents", "knowledge_chunks", "channel_accounts",
    "channel_credentials_metadata", "webhook_events", "notifications", "audit_logs",
    "ai_sessions", "ai_tool_calls", "alembic_version"
]

def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Only execute PostgreSQL RLS statements when on PostgreSQL
    if dialect != "postgresql":
        return

    # 1. Enable RLS on all 32 public tables
    for table in PUBLIC_TABLES:
        op.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;")

    # 2. Create helper function to lookup business memberships for auth.uid()
    op.execute("""
    CREATE OR REPLACE FUNCTION public.get_user_business_ids()
    RETURNS SETOF text
    LANGUAGE sql
    STABLE
    SECURITY DEFINER
    SET search_path = public
    AS $$
      SELECT business_id FROM public.business_members WHERE user_id = auth.uid()::text;
    $$;
    """)

    # 3. Create RLS Policies for Direct Tenant-Scoped Tables (for authenticated role)
    tenant_tables = [
        "businesses", "business_settings", "ai_settings", "product_categories",
        "products", "inventory", "customers", "conversations", "leads",
        "delivery_zones", "orders", "payments", "follow_up_jobs", "knowledge_documents",
        "knowledge_chunks", "channel_accounts", "notifications", "audit_logs"
    ]

    for table in tenant_tables:
        id_column = "id" if table == "businesses" else "business_id"
        op.execute(f"""
        CREATE POLICY tenant_isolation_policy_{table} ON public.{table}
        FOR ALL
        TO authenticated
        USING ({id_column} IN (SELECT public.get_user_business_ids()))
        WITH CHECK ({id_column} IN (SELECT public.get_user_business_ids()));
        """)

    # 4. Allow authenticated users to insert new businesses (for onboarding)
    op.execute("""
    CREATE POLICY business_onboarding_insert ON public.businesses
    FOR INSERT
    TO authenticated
    WITH CHECK (true);
    """)

    # 5. Policies for Users and Memberships
    op.execute("""
    CREATE POLICY users_self_access ON public.users
    FOR ALL
    TO authenticated
    USING (id = auth.uid()::text)
    WITH CHECK (id = auth.uid()::text);
    """)

    op.execute("""
    CREATE POLICY members_tenant_access ON public.business_members
    FOR ALL
    TO authenticated
    USING (business_id IN (SELECT public.get_user_business_ids()))
    WITH CHECK (business_id IN (SELECT public.get_user_business_ids()));
    """)

    # 6. Child tables joined via parent
    op.execute("""
    CREATE POLICY product_variants_tenant_policy ON public.product_variants
    FOR ALL
    TO authenticated
    USING (product_id IN (SELECT id FROM public.products WHERE business_id IN (SELECT public.get_user_business_ids())))
    WITH CHECK (product_id IN (SELECT id FROM public.products WHERE business_id IN (SELECT public.get_user_business_ids())));
    """)

    op.execute("""
    CREATE POLICY product_images_tenant_policy ON public.product_images
    FOR ALL
    TO authenticated
    USING (product_id IN (SELECT id FROM public.products WHERE business_id IN (SELECT public.get_user_business_ids())))
    WITH CHECK (product_id IN (SELECT id FROM public.products WHERE business_id IN (SELECT public.get_user_business_ids())));
    """)

    op.execute("""
    CREATE POLICY customer_addresses_tenant_policy ON public.customer_addresses
    FOR ALL
    TO authenticated
    USING (customer_id IN (SELECT id FROM public.customers WHERE business_id IN (SELECT public.get_user_business_ids())))
    WITH CHECK (customer_id IN (SELECT id FROM public.customers WHERE business_id IN (SELECT public.get_user_business_ids())));
    """)

    op.execute("""
    CREATE POLICY messages_tenant_policy ON public.messages
    FOR ALL
    TO authenticated
    USING (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT public.get_user_business_ids())))
    WITH CHECK (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT public.get_user_business_ids())));
    """)

    op.execute("""
    CREATE POLICY participants_tenant_policy ON public.conversation_participants
    FOR ALL
    TO authenticated
    USING (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT public.get_user_business_ids())))
    WITH CHECK (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT public.get_user_business_ids())));
    """)

    op.execute("""
    CREATE POLICY lead_events_tenant_policy ON public.lead_events
    FOR ALL
    TO authenticated
    USING (lead_id IN (SELECT id FROM public.leads WHERE business_id IN (SELECT public.get_user_business_ids())))
    WITH CHECK (lead_id IN (SELECT id FROM public.leads WHERE business_id IN (SELECT public.get_user_business_ids())));
    """)

    op.execute("""
    CREATE POLICY order_items_tenant_policy ON public.order_items
    FOR ALL
    TO authenticated
    USING (order_id IN (SELECT id FROM public.orders WHERE business_id IN (SELECT public.get_user_business_ids())))
    WITH CHECK (order_id IN (SELECT id FROM public.orders WHERE business_id IN (SELECT public.get_user_business_ids())));
    """)

    op.execute("""
    CREATE POLICY channel_credentials_tenant_policy ON public.channel_credentials_metadata
    FOR ALL
    TO authenticated
    USING (channel_account_id IN (SELECT id FROM public.channel_accounts WHERE business_id IN (SELECT public.get_user_business_ids())))
    WITH CHECK (channel_account_id IN (SELECT id FROM public.channel_accounts WHERE business_id IN (SELECT public.get_user_business_ids())));
    """)

    op.execute("""
    CREATE POLICY ai_sessions_tenant_policy ON public.ai_sessions
    FOR ALL
    TO authenticated
    USING (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT public.get_user_business_ids())))
    WITH CHECK (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT public.get_user_business_ids())));
    """)

    op.execute("""
    CREATE POLICY ai_tool_calls_tenant_policy ON public.ai_tool_calls
    FOR ALL
    TO authenticated
    USING (session_id IN (
        SELECT s.id FROM public.ai_sessions s
        JOIN public.conversations c ON s.conversation_id = c.id
        WHERE c.business_id IN (SELECT public.get_user_business_ids())
    ))
    WITH CHECK (session_id IN (
        SELECT s.id FROM public.ai_sessions s
        JOIN public.conversations c ON s.conversation_id = c.id
        WHERE c.business_id IN (SELECT public.get_user_business_ids())
    ));
    """)

    # 7. Public Read-Only Policies for Storefront / Anon Access (Products and Delivery Zones only)
    op.execute("""
    CREATE POLICY public_products_read ON public.products
    FOR SELECT
    TO anon
    USING (active = true);
    """)

    op.execute("""
    CREATE POLICY public_categories_read ON public.product_categories
    FOR SELECT
    TO anon
    USING (active = true);
    """)

    op.execute("""
    CREATE POLICY public_images_read ON public.product_images
    FOR SELECT
    TO anon
    USING (product_id IN (SELECT id FROM public.products WHERE active = true));
    """)

    op.execute("""
    CREATE POLICY public_variants_read ON public.product_variants
    FOR SELECT
    TO anon
    USING (product_id IN (SELECT id FROM public.products WHERE active = true));
    """)

    op.execute("""
    CREATE POLICY public_delivery_zones_read ON public.delivery_zones
    FOR SELECT
    TO anon
    USING (active = true);
    """)


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect != "postgresql":
        return

    # Drop policies
    for table in PUBLIC_TABLES:
        op.execute(f"ALTER TABLE public.{table} DISABLE ROW LEVEL SECURITY;")
    op.execute("DROP FUNCTION IF EXISTS public.get_user_business_ids();")
