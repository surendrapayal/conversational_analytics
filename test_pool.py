import asyncio
import psycopg_pool

async def test():
    print("Opening pool...")
    pool = psycopg_pool.AsyncConnectionPool(
        "postgresql://admin_user:admin_password@localhost:5434/agent_memory",
        min_size=1,
        kwargs={"autocommit": True, "prepare_threshold": 0},
        open=False,
    )
    await asyncio.wait_for(pool.open(wait=True), timeout=10.0)
    print("Pool opened OK")
    async with pool.connection() as conn:
        result = await conn.execute("SELECT 1")
        row = await result.fetchone()
        print(f"Query result: {row}")
    await pool.close()
    print("Done")

asyncio.run(test())
