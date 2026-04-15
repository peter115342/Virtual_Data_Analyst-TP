import json
from typing import Any

from redis.asyncio import Redis, from_url

from app.config import settings

_client: Redis | None = None


async def connect() -> None:
	"""Connect to Redis. Failures are tolerated (best-effort caching)."""
	global _client
	if _client is not None:
		return

	try:
		_client = from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
		await _client.ping()
		print(f"Redis connected: {settings.redis_url}")
	except Exception as exc:
		_client = None
		print(f"Redis unavailable, continuing without cache: {exc}")


async def disconnect() -> None:
	"""Close Redis connection if it exists."""
	global _client
	if _client is None:
		return

	try:
		await _client.aclose()
		print("Redis disconnected")
	except Exception as exc:
		print(f"Redis disconnect warning: {exc}")
	finally:
		_client = None


def is_connected() -> bool:
	return _client is not None


async def get_json(key: str) -> dict[str, Any] | list[Any] | None:
	"""Read and deserialize JSON value from cache."""
	if _client is None:
		return None

	try:
		raw_value = await _client.get(key)
		if raw_value is None:
			return None
		return json.loads(raw_value)
	except Exception as exc:
		print(f"Redis GET warning for key '{key}': {exc}")
		return None


async def set_json(key: str, value: Any, ttl_seconds: int | None = None) -> bool:
	"""Serialize and store JSON value in cache."""
	if _client is None:
		return False

	try:
		payload = json.dumps(value, default=str)
		if ttl_seconds and ttl_seconds > 0:
			await _client.set(key, payload, ex=ttl_seconds)
		else:
			await _client.set(key, payload)
		return True
	except Exception as exc:
		print(f"Redis SET warning for key '{key}': {exc}")
		return False


async def incr(key: str, amount: int = 1) -> int | None:
	"""Increment numeric key and return its new value."""
	if _client is None:
		return None

	try:
		return int(await _client.incrby(key, amount))
	except Exception as exc:
		print(f"Redis INCR warning for key '{key}': {exc}")
		return None


async def get_int(key: str) -> int | None:
	"""Read integer key value."""
	if _client is None:
		return None

	try:
		raw_value = await _client.get(key)
		if raw_value is None:
			return None
		return int(raw_value)
	except Exception as exc:
		print(f"Redis GET INT warning for key '{key}': {exc}")
		return None


async def count_pattern(pattern: str) -> int:
	"""Count keys matching a Redis pattern."""
	if _client is None:
		return 0

	try:
		count = 0
		async for _key in _client.scan_iter(match=pattern):
			count += 1
		return count
	except Exception as exc:
		print(f"Redis count pattern warning for '{pattern}': {exc}")
		return 0


async def delete_pattern(pattern: str) -> int:
	"""Delete keys by pattern and return number of removed keys."""
	if _client is None:
		return 0

	try:
		deleted = 0
		async for key in _client.scan_iter(match=pattern):
			deleted += await _client.delete(key)
		return deleted
	except Exception as exc:
		print(f"Redis delete pattern warning for '{pattern}': {exc}")
		return 0

