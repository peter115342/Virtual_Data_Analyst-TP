# Document schema (collection: "sessions"):
# {
#   _id: ObjectId (auto),
#   session_id: str (UUID — one per DB connection),
#   user_id: str,
#   db_type: str,
#   db_host: str,
#   db_name: str,
#   connected_at: datetime,
#   disconnected_at: datetime | None,
#   messages: [
#     {
#       role: "user" | "assistant",
#       content: str,
#       sql_query: str | None,
#       row_count: int | None,
#       timestamp: datetime,
#     }
#   ]
# }
#
# Indexes:
#   - (user_id, connected_at DESC) — list sessions for a user
#   - (session_id) — unique, fast lookup

import uuid
from datetime import datetime, timezone

from app.database.mongo import get_db

COLLECTION = "sessions"


async def ensure_indexes():
    col = get_db()[COLLECTION]
    await col.create_index("session_id", unique=True)
    await col.create_index([("user_id", 1), ("connected_at", -1)])


async def create_session(
    user_id: str,
    db_type: str,
    db_host: str,
    db_name: str,
) -> str:
    session_id = str(uuid.uuid4())
    doc = {
        "session_id": session_id,
        "user_id": user_id,
        "db_type": db_type,
        "db_host": db_host,
        "db_name": db_name,
        "connected_at": datetime.now(timezone.utc),
        "disconnected_at": None,
        "messages": [],
    }
    col = get_db()[COLLECTION]
    await col.insert_one(doc)
    return session_id


async def close_session(session_id: str):
    col = get_db()[COLLECTION]
    await col.update_one(
        {"session_id": session_id},
        {"$set": {"disconnected_at": datetime.now(timezone.utc)}},
    )


async def add_message(
    session_id: str,
    role: str,
    content: str,
    sql_query: str | None = None,
    row_count: int | None = None,
    success: bool | None = None,
):
    msg = {
        "role": role,
        "content": content,
        "sql_query": sql_query,
        "row_count": row_count,
        "timestamp": datetime.now(timezone.utc),
        "success": success,
    }
    col = get_db()[COLLECTION]
    await col.update_one(
        {"session_id": session_id},
        {"$push": {"messages": msg}},
    )


async def get_session(session_id: str) -> dict | None:
    col = get_db()[COLLECTION]
    return await col.find_one({"session_id": session_id}, {"_id": 0})


async def list_user_sessions(user_id: str, limit: int = 50) -> list[dict]:
    col = get_db()[COLLECTION]
    cursor = (
        col.find(
            {"user_id": user_id},
            {"_id": 0, "messages": 0},
        )
        .sort("connected_at", -1)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)
