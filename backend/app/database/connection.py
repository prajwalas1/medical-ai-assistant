import asyncpg
from app.core.config import settings


pool = None
async def connect_to_database():
    global pool

    pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=10,
    )
    print("✅ Connected to Neon PostgreSQL")


async def disconnect_database():
    global pool
    
    if pool:
        await pool.close()
        pool = None
        print("🔴 Database connection closed")

