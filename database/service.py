from socket import gaierror

from decouple import config

from aioredis import create_redis_pool
from aioredis.errors import ConnectionClosedError

REDIS_URL = config("REDIS_URL", "redis://localhost:6379")

redis_pool = None


async def get_redis_pool():
    global redis_pool
    if redis_pool is None:
        try:
            redis_pool = await create_redis_pool(REDIS_URL)
        except (OSError, gaierror):
            raise ConnectionClosedError("Redis offline")
    return redis_pool


async def startup():
    await get_redis_pool()


async def shutdown():
    redis_pool.close()
    await redis_pool.wait_closed()


async def get_data(key):
    _redis_pool = await get_redis_pool()
    return await _redis_pool.get(key)


async def set_data(key, value):
    _redis_pool = await get_redis_pool()
    await _redis_pool.set(key, value)
