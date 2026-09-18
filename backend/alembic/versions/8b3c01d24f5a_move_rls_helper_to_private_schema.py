"""move_rls_helper_to_private_schema

Revision ID: 8b3c01d24f5a
Revises: 7a2b90c13e4f
Create Date: 2026-09-18 11:46:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '8b3c01d24f5a'
down_revision: Union[str, Sequence[str], None] = '7a2b90c13e4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DIRECT_TENANT_TABLES = [
    "businesses", "business_settings", "ai_settings", "product_categories",
    "products", "inventory", "customers", "conversations", "leads",
    "delivery_zones", "orders", "payments", "follow_up_jobs", "knowledge_documents",
    "knowledge_chunks", "channel_accounts", "notifications", "audit_logs"
]

def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect != "postgresql":
        return

    # 1. Create private schema for internal security helpers
    op.execute("""
    CREATE SCHEMA IF NOT EXISTS app_security;
    REVOKE ALL ON SCHEMA app_security FROM PUBLIC;
    REVOKE ALL ON SCHEMA app_security FROM anon;
    GRANT USAGE ON SCHEMA app_security TO authenticated;
    GRANT USAGE ON SCHEMA app_security TO service_role;
    """)

    # 2. Create the helper inside app_security schema with safe search_path
    op.execute("""
    CREATE OR REPLACE FUNCTION app_security.get_user_business_ids()
    RETURNS SETOF text
    LANGUAGE sql
    STABLE
    SECURITY DEFINER
    SET search_path = public
    AS $$
      SELECT business_id FROM public.business_members WHERE user_id = auth.uid()::text;
    $$;

    REVOKE ALL ON FUNCTION app_security.get_user_business_ids() FROM PUBLIC;
    REVOKE ALL ON FUNCTION app_security.get_user_business_ids() FROM anon;
    GRANT EXECUTE ON FUNCTION app_security.get_user_business_ids() TO authenticated;
    GRANT EXECUTE ON FUNCTION app_security.get_user_business_ids() TO service_role;
    """)

    # 3. Update all direct tenant RLS policies to use app_security.get_user_business_ids()
    for table in DIRECT_TENANT_TABLES:
        id_column = "id" if table == "businesses" else "business_id"
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_policy_{table} ON public.{table};")
        op.execute(f"""
        CREATE POLICY tenant_isolation_policy_{table} ON public.{table}
        FOR ALL
        TO authenticated
        USING ({id_column} IN (SELECT app_security.get_user_business_ids()))
        WITH CHECK ({id_column} IN (SELECT app_security.get_user_business_ids()));
        """)

    # 4. Update business_members policy
    op.execute("DROP POLICY IF EXISTS members_tenant_access ON public.business_members;")
    op.execute("""
    CREATE POLICY members_tenant_access ON public.business_members
    FOR ALL
    TO authenticated
    USING (business_id IN (SELECT app_security.get_user_business_ids()))
    WITH CHECK (business_id IN (SELECT app_security.get_user_business_ids()));
    """)

    # 5. Update child table policies
    op.execute("DROP POLICY IF EXISTS product_variants_tenant_policy ON public.product_variants;")
    op.execute("""
    CREATE POLICY product_variants_tenant_policy ON public.product_variants
    FOR ALL
    TO authenticated
    USING (product_id IN (SELECT id FROM public.products WHERE business_id IN (SELECT app_security.get_user_business_ids())))
    WITH CHECK (product_id IN (SELECT id FROM public.products WHERE business_id IN (SELECT app_security.get_user_business_ids())));
    """)

    op.execute("DROP POLICY IF EXISTS product_images_tenant_policy ON public.product_images;")
    op.execute("""
    CREATE POLICY product_images_tenant_policy ON public.product_images
    FOR ALL
    TO authenticated
    USING (product_id IN (SELECT id FROM public.products WHERE business_id IN (SELECT app_security.get_user_business_ids())))
    WITH CHECK (product_id IN (SELECT id FROM public.products WHERE business_id IN (SELECT app_security.get_user_business_ids())));
    """)

    op.execute("DROP POLICY IF EXISTS customer_addresses_tenant_policy ON public.customer_addresses;")
    op.execute("""
    CREATE POLICY customer_addresses_tenant_policy ON public.customer_addresses
    FOR ALL
    TO authenticated
    USING (customer_id IN (SELECT id FROM public.customers WHERE business_id IN (SELECT app_security.get_user_business_ids())))
    WITH CHECK (customer_id IN (SELECT id FROM public.customers WHERE business_id IN (SELECT app_security.get_user_business_ids())));
    """)

    op.execute("DROP POLICY IF EXISTS messages_tenant_policy ON public.messages;")
    op.execute("""
    CREATE POLICY messages_tenant_policy ON public.messages
    FOR ALL
    TO authenticated
    USING (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT app_security.get_user_business_ids())))
    WITH CHECK (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT app_security.get_user_business_ids())));
    """)

    op.execute("DROP POLICY IF EXISTS participants_tenant_policy ON public.conversation_participants;")
    op.execute("""
    CREATE POLICY participants_tenant_policy ON public.conversation_participants
    FOR ALL
    TO authenticated
    USING (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT app_security.get_user_business_ids())))
    WITH CHECK (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT app_security.get_user_business_ids())));
    """)

    op.execute("DROP POLICY IF EXISTS lead_events_tenant_policy ON public.lead_events;")
    op.execute("""
    CREATE POLICY lead_events_tenant_policy ON public.lead_events
    FOR ALL
    TO authenticated
    USING (lead_id IN (SELECT id FROM public.leads WHERE business_id IN (SELECT app_security.get_user_business_ids())))
    WITH CHECK (lead_id IN (SELECT id FROM public.leads WHERE business_id IN (SELECT app_security.get_user_business_ids())));
    """)

    op.execute("DROP POLICY IF EXISTS order_items_tenant_policy ON public.order_items;")
    op.execute("""
    CREATE POLICY order_items_tenant_policy ON public.order_items
    FOR ALL
    TO authenticated
    USING (order_id IN (SELECT id FROM public.orders WHERE business_id IN (SELECT app_security.get_user_business_ids())))
    WITH CHECK (order_id IN (SELECT id FROM public.orders WHERE business_id IN (SELECT app_security.get_user_business_ids())));
    """)

    op.execute("DROP POLICY IF EXISTS channel_credentials_tenant_policy ON public.channel_credentials_metadata;")
    op.execute("""
    CREATE POLICY channel_credentials_tenant_policy ON public.channel_credentials_metadata
    FOR ALL
    TO authenticated
    USING (channel_account_id IN (SELECT id FROM public.channel_accounts WHERE business_id IN (SELECT app_security.get_user_business_ids())))
    WITH CHECK (channel_account_id IN (SELECT id FROM public.channel_accounts WHERE business_id IN (SELECT app_security.get_user_business_ids())));
    """)

    op.execute("DROP POLICY IF EXISTS ai_sessions_tenant_policy ON public.ai_sessions;")
    op.execute("""
    CREATE POLICY ai_sessions_tenant_policy ON public.ai_sessions
    FOR ALL
    TO authenticated
    USING (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT app_security.get_user_business_ids())))
    WITH CHECK (conversation_id IN (SELECT id FROM public.conversations WHERE business_id IN (SELECT app_security.get_user_business_ids())));
    """)

    op.execute("DROP POLICY IF EXISTS ai_tool_calls_tenant_policy ON public.ai_tool_calls;")
    op.execute("""
    CREATE POLICY ai_tool_calls_tenant_policy ON public.ai_tool_calls
    FOR ALL
    TO authenticated
    USING (session_id IN (
        SELECT s.id FROM public.ai_sessions s
        JOIN public.conversations c ON s.conversation_id = c.id
        WHERE c.business_id IN (SELECT app_security.get_user_business_ids())
    ))
    WITH CHECK (session_id IN (
        SELECT s.id FROM public.ai_sessions s
        JOIN public.conversations c ON s.conversation_id = c.id
        WHERE c.business_id IN (SELECT app_security.get_user_business_ids())
    ));
    """)

    # 6. Drop the old function from public schema completely
    op.execute("DROP FUNCTION IF EXISTS public.get_user_business_ids();")


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect != "postgresql":
        return

    # Recreate in public schema
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

    for table in DIRECT_TENANT_TABLES:
        id_column = "id" if table == "businesses" else "business_id"
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_policy_{table} ON public.{table};")
        op.execute(f"""
        CREATE POLICY tenant_isolation_policy_{table} ON public.{table}
        FOR ALL
        TO authenticated
        USING ({id_column} IN (SELECT public.get_user_business_ids()))
        WITH CHECK ({id_column} IN (SELECT public.get_user_business_ids()));
        """)

    op.execute("DROP SCHEMA IF EXISTS app_security CASCADE;")
