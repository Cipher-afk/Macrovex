from datetime import datetime
from pathlib import Path
import json
from pprint import pprint
from dataclasses import dataclass
from redis.asyncio import Redis

date = datetime.now().isoformat()
BASE_DIR = Path(__file__).resolve().parent


def isholiday(date: datetime):
    if date.weekday() > 5:
        return True
    else:
        return False


def read_json(json_file: Path):
    with open(json_file, "r") as file:
        data = json.loads(file.read())
        return data

@dataclass(kw_only=True)
class GroqRateLimiter:
    redis_client: Redis
    max_per_minute: int = 25
    max_per_day: int = 900
    minute_key: str = "groq:rl:minute"
    day_key: str = "groq:rl:day"

    async def acquire(self) -> tuple[bool, str]:
        minute_count = await self.redis_client.get(self.minute_key)
        daily_count = await self.redis_client.get(self.day_key)
        minute_count = int(minute_count) if minute_count else 0
        daily_count = int(daily_count) if daily_count else 0
        if minute_count > self.max_per_minute:
            return (False, "minute")
        if daily_count > self.max_per_day:
            return (False, "daily")
        pipe = self.redis_client.pipeline()
        pipe.incr(self.minute_key)
        pipe.expire(self.minute_key, 60, nx=True)
        pipe.incr(self.day_key)
        pipe.expire(self.day_key, 86400, nx=True)
        await pipe.execute()
        return (True, "")

    async def seconds_until_minute(self) -> int:
        ttl = await self.redis_client.ttl(self.minute_key)
        return max(ttl, 1)

if __name__ == "__main__":
    print(isholiday(date=datetime.fromisoformat(date)))
    data = read_json(Path(BASE_DIR, "calendar.json"))
    pprint(data)
