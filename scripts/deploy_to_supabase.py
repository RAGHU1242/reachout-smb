import sys
import os
import subprocess

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.core.config import settings

def main():
    print("=" * 60)
    print("ReachOut SMB - Supabase PostgreSQL Migration & Setup")
    print("=" * 60)
    
    db_url = settings.DATABASE_URL
    print(f"Configured SUPABASE_URL: {settings.SUPABASE_URL}")
    
    if "[YOUR-PASSWORD]" in db_url:
        print("\n[ATTENTION REQUIRED]")
        print("Please edit your local `.env` file at `C:\\Raghu\\AI Sales & Order Assistant\\.env`")
        print("Replace `[YOUR-PASSWORD]` in DATABASE_URL with your Supabase database password:")
        print("DATABASE_URL=postgresql+asyncpg://postgres:<your_password>@db.bqwmgdxaynsxabgxgnos.supabase.co:5432/postgres\n")
        sys.exit(1)
        
    print(f"Connecting to: {db_url.split('@')[-1] if '@' in db_url else db_url}")

    # 1. Run Alembic Migrations
    print("\n[Step 1/3] Running Alembic Migrations against Supabase...")
    res = subprocess.run(["alembic", "-c", "alembic.ini", "upgrade", "head"], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("Migration Error:", res.stderr)
        sys.exit(res.returncode)
    print("✓ Alembic Migrations successfully applied to Supabase!")

    # 2. Check 31 Application Tables
    print("\n[Step 2/3] Verifying all 31 application tables...")
    check_res = subprocess.run([sys.executable, "scripts/migrate_and_seed_supabase.py"], capture_output=True, text=True)
    print(check_res.stdout)
    if check_res.returncode != 0:
        print("Table Check Error:", check_res.stderr)
        sys.exit(check_res.returncode)

    # 3. Seed Rani Fashions Demo Data
    print("\n[Step 3/3] Seeding Rani Fashions demo data...")
    seed_res = subprocess.run([sys.executable, "scripts/seed_demo_data.py"], capture_output=True, text=True)
    print(seed_res.stdout)
    if seed_res.returncode != 0:
        print("Seed Error:", seed_res.stderr)
        sys.exit(seed_res.returncode)
    print("✓ Rani Fashions demo data seeded successfully!")

    print("\n" + "=" * 60)
    print("Supabase PostgreSQL Setup Completed Successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
