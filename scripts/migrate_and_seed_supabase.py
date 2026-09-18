import sys
import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.core.config import settings

EXPECTED_TABLES = [
    "users", "businesses", "business_members", "business_settings", "ai_settings",
    "product_categories", "products", "product_variants", "product_images", "inventory",
    "customers", "customer_addresses", "conversations", "conversation_participants", "messages",
    "leads", "lead_events", "delivery_zones", "orders", "order_items", "payments",
    "follow_up_jobs", "knowledge_documents", "knowledge_chunks", "channel_accounts",
    "channel_credentials_metadata", "webhook_events", "notifications", "audit_logs",
    "ai_sessions", "ai_tool_calls"
]

async def verify_and_check():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"Connecting to database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    engine = create_async_engine(db_url, echo=False)
    
    try:
        async with engine.connect() as conn:
            # Check connection
            if "sqlite" in db_url:
                res = await conn.execute(text("SELECT 1;"))
                print(f"Connected successfully to local SQLite DB!")
                query = text("SELECT name FROM sqlite_master WHERE type='table';")
            else:
                res = await conn.execute(text("SELECT current_database(), current_user;"))
                db_name, user = res.first()
                print(f"Connected successfully to Supabase DB '{db_name}' as user '{user}'!")
                query = text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
            
            tables_res = await conn.execute(query)
            tables = [r[0] for r in tables_res.fetchall()]
            print(f"Found {len(tables)} tables in database:")
            for t in sorted(tables):
                print(f"  - {t}")

            missing = [t for t in EXPECTED_TABLES if t not in tables]
            if missing:
                print(f"\nMissing tables ({len(missing)}): {missing}")
            else:
                print(f"\nALL {len(EXPECTED_TABLES)} EXPECTED APPLICATION TABLES ARE PRESENT!")

            return len(tables), missing
    except Exception as e:
        print(f"Connection failed: {type(e).__name__}: {e}")
        return 0, EXPECTED_TABLES
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_and_check())
