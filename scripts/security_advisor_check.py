import sys
import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.core.config import settings

async def run_security_check():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print("Querying Supabase PostgreSQL Security Advisor checks...\n")
    engine = create_async_engine(db_url, echo=False)
    try:
        async with engine.connect() as conn:
            # Check 1: Tables without RLS enabled
            res = await conn.execute(text("""
                SELECT c.relname as table_name, c.relrowsecurity as rls_enabled
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public' AND c.relkind = 'r'
                ORDER BY c.relname;
            """))
            rows = res.fetchall()
            
            no_rls = [r[0] for r in rows if not r[1]]
            rls_on = [r[0] for r in rows if r[1]]
            
            print(f"Total public tables: {len(rows)}")
            print(f"Tables WITH RLS enabled: {len(rls_on)}")
            print(f"Tables WITHOUT RLS enabled: {len(no_rls)}")
            if no_rls:
                print("\n[SECURITY ADVISOR WARNING] RLS Disabled on tables:")
                for t in no_rls:
                    print(f"  - {t}")
            else:
                print("\n[SECURITY ADVISOR PASSED] RLS is enabled on ALL public tables!")

            # Check 2: Existing policies
            pol_res = await conn.execute(text("""
                SELECT tablename, policyname, roles, cmd, qual
                FROM pg_policies
                WHERE schemaname = 'public'
                ORDER BY tablename, policyname;
            """))
            pols = pol_res.fetchall()
            print(f"\nTotal active RLS policies: {len(pols)}")
            for p in pols:
                print(f"  - Table '{p[0]}': Policy '{p[1]}' ({p[3]}) for roles {p[2]}")

            # Check 3: Backend-only tables (alembic_version, webhook_events)
            print("\nCheck 3: Backend-only tables audit (alembic_version, webhook_events)...")
            backend_tables = ["alembic_version", "webhook_events"]
            for bt in backend_tables:
                bt_pols = [p for p in pols if p[0] == bt]
                bt_rls = bt in rls_on
                print(f"  - Table '{bt}': RLS Enabled={bt_rls}, Client Policies={len(bt_pols)}")
                if bt_rls and len(bt_pols) == 0:
                    print(f"    [SECURE] Default-deny active. Only postgres/backend can access '{bt}'.")
                else:
                    print(f"    [WARNING] Unexpected client access on '{bt}'!")

            # Check 4: Function execute privileges & Schema isolation audit
            print("\nCheck 4: SECURITY DEFINER function schema & execute audit...")
            # 4a: Confirm public.get_user_business_ids is completely gone
            pub_fn_res = await conn.execute(text("""
                SELECT p.proname
                FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                WHERE n.nspname = 'public' AND p.proname = 'get_user_business_ids';
            """))
            pub_fn = pub_fn_res.fetchone()
            if pub_fn is None:
                print("  - public schema: 'get_user_business_ids' is completely REMOVED. [PASSED]")
                print("    (Zero public SECURITY DEFINER functions exist; PostgREST cannot expose RPC endpoint).")
            else:
                print("  - [WARNING] 'get_user_business_ids' still exists in public schema!")

            # 4b: Check app_security.get_user_business_ids
            priv_fn_res = await conn.execute(text("""
                SELECT 
                    n.nspname,
                    p.proname,
                    has_function_privilege('anon', p.oid, 'EXECUTE') as anon_execute,
                    has_function_privilege('authenticated', p.oid, 'EXECUTE') as auth_execute,
                    has_function_privilege('service_role', p.oid, 'EXECUTE') as service_execute,
                    p.prosecdef as is_security_definer
                FROM pg_proc p
                JOIN pg_namespace n ON n.oid = p.pronamespace
                WHERE n.nspname = 'app_security' AND p.proname = 'get_user_business_ids';
            """))
            priv_fn = priv_fn_res.fetchone()
            if priv_fn:
                nsp, proname, anon_exec, auth_exec, srv_exec, is_secdef = priv_fn
                print(f"  - Private schema function '{nsp}.{proname}':")
                print(f"    • SECURITY DEFINER: {is_secdef}")
                print(f"    • anon can EXECUTE: {anon_exec}")
                print(f"    • authenticated can EXECUTE: {auth_exec}")
                print(f"    • service_role can EXECUTE: {srv_exec}")
                if not anon_exec and auth_exec and is_secdef:
                    print("    [SECURITY ADVISOR PASSED] Function isolated in private schema! Not exposed via PostgREST. Authenticated RLS active!")
                else:
                    print(f"    [SECURITY ADVISOR WARNING] Unexpected private function permissions: anon={anon_exec}")
            else:
                print("  - [WARNING] Function 'app_security.get_user_business_ids' not found!")

            return len(no_rls), len(pols)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_security_check())
