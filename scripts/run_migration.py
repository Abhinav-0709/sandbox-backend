"""
Direct migration and environment re-seed script.
Adds subrole_id and subrole_title columns to sandbox_environments if they do not exist,
then seeds/updates all builtin environments.
"""
import asyncio
import sys
from pathlib import Path

# Add backend root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.database import AsyncSessionLocal, engine
from app.services.environment_service import EnvironmentService


async def migrate_and_seed():
    print(f"[MIGRATION] Connecting to database...")
    async with engine.begin() as conn:
        print("[MIGRATION] Adding subrole columns to sandbox_environments if missing...")
        await conn.execute(text(
            "ALTER TABLE sandbox_environments ADD COLUMN IF NOT EXISTS subrole_id VARCHAR(100);"
        ))
        await conn.execute(text(
            "ALTER TABLE sandbox_environments ADD COLUMN IF NOT EXISTS subrole_title VARCHAR(100);"
        ))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_sandbox_environments_subrole_id ON sandbox_environments (subrole_id);"
        ))
        print("[MIGRATION] Schema successfully updated!")

    print("[MIGRATION] Re-seeding / updating builtin environments...")
    async with AsyncSessionLocal() as session:
        service = EnvironmentService(session)
        await service.ensure_defaults()
        await session.commit()
        print(f"[MIGRATION] Successfully updated environments with subrole metadata.")


if __name__ == "__main__":
    asyncio.run(migrate_and_seed())
