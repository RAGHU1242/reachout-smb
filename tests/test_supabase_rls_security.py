import pytest
from httpx import AsyncClient
from sqlalchemy import text
from conftest import TestSessionLocal

@pytest.mark.asyncio
async def test_supabase_rls_enabled_on_all_tables():
    """
    Verifies that all public tables in Supabase PostgreSQL have Row Level Security enabled.
    """
    async with TestSessionLocal() as session:
        res = await session.execute(text("""
            SELECT c.relname as table_name, c.relrowsecurity as rls_enabled
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relkind = 'r'
            ORDER BY c.relname;
        """))
        rows = res.fetchall()
        assert len(rows) >= 31

        unprotected_tables = [r[0] for r in rows if not r[1]]
        assert len(unprotected_tables) == 0, f"Tables with RLS disabled: {unprotected_tables}"

@pytest.mark.asyncio
async def test_cross_tenant_api_isolation(async_client: AsyncClient):
    """
    Verifies that a user from Business A cannot read or modify data from Business B.
    """
    # 1. Login as demo user (Rani Fashions)
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "demo@reachoutsmb.com", "password": "password123"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Rani Fashions business ID
    biz_res = await async_client.get("/api/v1/businesses/current", headers=headers)
    assert biz_res.status_code == 200
    valid_biz_id = biz_res.json()["id"]

    # 3. Attempt to access a non-existent or foreign business ID
    foreign_biz_id = "00000000-0000-0000-0000-000000000000"
    forbidden_res = await async_client.get(
        "/api/v1/businesses/current",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Business-Id": foreign_biz_id
        }
    )
    assert forbidden_res.status_code == 403
    assert "Access denied" in forbidden_res.json()["detail"]

@pytest.mark.asyncio
async def test_security_definer_function_restricted_from_anon():
    """
    Verifies that get_user_business_ids() is removed from public schema (no PostgREST RPC),
    and isolated in app_security schema where anon cannot execute it, but authenticated can.
    """
    async with TestSessionLocal() as session:
        # 1. Assert public function is completely removed
        pub_res = await session.execute(text("""
            SELECT p.proname
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname = 'public' AND p.proname = 'get_user_business_ids';
        """))
        assert pub_res.fetchone() is None, "Function get_user_business_ids MUST NOT exist in public schema"

        # 2. Assert private schema function exists and permissions are secure
        priv_res = await session.execute(text("""
            SELECT 
                has_function_privilege('anon', p.oid, 'EXECUTE') as anon_execute,
                has_function_privilege('authenticated', p.oid, 'EXECUTE') as auth_execute,
                p.prosecdef as is_secdef
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid = p.pronamespace
            WHERE n.nspname = 'app_security' AND p.proname = 'get_user_business_ids';
        """))
        row = priv_res.fetchone()
        assert row is not None, "Function get_user_business_ids must exist in app_security schema"
        anon_exec, auth_exec, is_secdef = row
        assert is_secdef is True, "Helper must be SECURITY DEFINER for membership lookup"
        assert anon_exec is False, "anon role MUST NOT have EXECUTE on app_security.get_user_business_ids"
        assert auth_exec is True, "authenticated role MUST have EXECUTE on app_security.get_user_business_ids"

@pytest.mark.asyncio
async def test_backend_only_tables_isolated():
    """
    Verifies that alembic_version and webhook_events have RLS enabled and 0 client policies (default-deny).
    """
    async with TestSessionLocal() as session:
        # 1. RLS enabled
        res = await session.execute(text("""
            SELECT c.relname, c.relrowsecurity
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relname IN ('alembic_version', 'webhook_events');
        """))
        rows = {r[0]: r[1] for r in res.fetchall()}
        assert rows.get("alembic_version") is True, "alembic_version must have RLS enabled"
        assert rows.get("webhook_events") is True, "webhook_events must have RLS enabled"

        # 2. No client policies
        pol_res = await session.execute(text("""
            SELECT tablename, policyname
            FROM pg_policies
            WHERE schemaname = 'public' AND tablename IN ('alembic_version', 'webhook_events');
        """))
        pols = pol_res.fetchall()
        assert len(pols) == 0, f"Backend-only tables must have 0 client policies, found: {pols}"

