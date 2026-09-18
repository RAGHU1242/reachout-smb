import sys
import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.core.config import settings

async def test_conn():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print("Connecting to Supabase PostgreSQL...")
    engine = create_async_engine(db_url, echo=False)
    try:
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT current_database(), current_user, version();"))
            db_name, user, ver = res.first()
            print(f"Connected successfully to DB: {db_name}")
            print(f"Authenticated as user: {user}")
            print(f"Server version: {ver.split()[0]} {ver.split()[1]}")
    except Exception as e:
        print(f"Connection failed: {type(e).__name__}: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_conn())
