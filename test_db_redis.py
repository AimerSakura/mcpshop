# test_db_redis.py
import os
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import redis.asyncio as redis_async
from dotenv import load_dotenv

load_dotenv()  # 自动从 .env 读取 DATABASE_URL/REDIS_URL

async def test_postgres():
    url = os.getenv("DATABASE_URL")
    print("Testing Postgres at:", url)
    engine = create_async_engine(url)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Postgres test query result:", result.scalar())
    except Exception as e:
        print("Postgres connection failed:", e)
    finally:
        await engine.dispose()

async def test_redis():
    url = os.getenv("REDIS_URL")
    print("Testing Redis at:", url)
    try:
        client = redis_async.from_url(url)
        pong = await client.ping()
        print("Redis PING response:", pong)
        await client.aclose()
    except Exception as e:
        print("Redis connection failed:", e)

async def main():
    await test_postgres()
    await test_redis()

if __name__ == "__main__":
    asyncio.run(main())
