from redis.asyncio import Redis
from config import settings
import asyncio

red = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)


async def save_summary(title, summary):
    await red.hset("ai_summary", mapping={title: summary})


async def get_summary(title: str):
    summaries = await red.hgetall("ai_summary")
    print(summaries.keys())
    if title not in summaries.keys():
        return False
    summary = await red.hget("ai_summary", title)
    return summary


if __name__ == "__main__":

    async def main():
        if await red.ping():
            print("yaay")
        else:
            print("naay")

    asyncio.run(main())
