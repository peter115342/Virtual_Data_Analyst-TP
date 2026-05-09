from typing import cast

import pytest

from app.api import routes
from app.database import connection, mongo


class FakeDbManager:
    def __init__(self, schema=None, data=None):
        self.schema = schema or {"table": [{"column": "id", "type": "int", "nullable": False}]}
        self.data = data or [{"id": 1}]
        self.connected = False
        self.disconnected = False

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.disconnected = True

    async def get_schema(self):
        return self.schema

    async def execute_query(self, sql):
        return self.data

    async def get_db_dialect(self):
        return "postgresql"


class FakeCursor:
    def __init__(self, docs):
        self._docs = list(docs)
        self._iter = iter(self._docs)

    def sort(self, *_args, **_kwargs):
        return self

    def __aiter__(self):
        self._iter = iter(self._docs)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class FakeCollection:
    def __init__(self, docs):
        self._docs = docs

    def find(self, *_args, **_kwargs):
        return FakeCursor(self._docs)


class FakeMongoDb:
    def __init__(self, docs):
        self._docs = docs

    def __getitem__(self, _name):
        return FakeCollection(self._docs)


@pytest.mark.asyncio
async def test_root_ok(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health_not_connected(client, monkeypatch):
    def raise_not_connected():
        raise RuntimeError("MongoDB is not connected")

    monkeypatch.setattr(mongo, "get_db", raise_not_connected)

    response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["database"] == "not initialized"
    assert body["mongodb"] == "not connected"


@pytest.mark.asyncio
async def test_generate_sql_success(client, monkeypatch):
    async def fake_generate_query(_self, _question, _schema, _dialect):
        return "SELECT 1"

    class FakeGenerator:
        generate_query = fake_generate_query

    monkeypatch.setattr(routes, "get_db_manager", lambda: FakeDbManager())
    monkeypatch.setattr(routes, "QueryGenerator", FakeGenerator)

    response = await client.post("/api/generate-sql", json={"question": "test"})

    assert response.status_code == 200
    assert response.json()["sql_query"] == "SELECT 1"


@pytest.mark.asyncio
async def test_ask_success_with_history(client, monkeypatch):
    async def fake_generate_query(_self, _question, _schema, _dialect):
        return "SELECT 2"

    async def fake_summarize(_self, sql_query, data, context):
        assert sql_query == "SELECT 2"
        assert context == "question"
        return "summary"

    history_calls = {"messages": []}

    async def fake_add_message(**kwargs):
        history_calls["messages"].append(kwargs)

    class FakeGenerator:
        generate_query = fake_generate_query

    class FakeSummarizer:
        summarize_query_results = fake_summarize

    monkeypatch.setattr(routes, "get_db_manager", lambda: FakeDbManager())
    monkeypatch.setattr(routes, "QueryGenerator", FakeGenerator)
    monkeypatch.setattr(routes, "ResponseSummarizer", FakeSummarizer)
    monkeypatch.setattr(routes.chat_history, "add_message", fake_add_message)

    response = await client.post("/api/ask", json={"question": "question", "session_id": "s-1"})

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "summary"
    assert body["row_count"] == 1
    assert body["session_id"] == "s-1"
    assert len(history_calls["messages"]) == 2


@pytest.mark.asyncio
async def test_query_and_summarize_success(client, monkeypatch):
    async def fake_summarize(_self, sql_query, data, context):
        assert sql_query == "SELECT 3"
        assert context == "ctx"
        return "summary"

    class FakeSummarizer:
        summarize_query_results = fake_summarize

    monkeypatch.setattr(routes, "get_db_manager", lambda: FakeDbManager())
    monkeypatch.setattr(routes, "ResponseSummarizer", FakeSummarizer)

    response = await client.post(
        "/api/query-and-summarize", json={"sql_query": "SELECT 3", "context": "ctx"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "summary"
    assert body["row_count"] == 1


@pytest.mark.asyncio
async def test_query_and_summarize_value_error(client, monkeypatch):
    class BadDbManager(FakeDbManager):
        async def execute_query(self, sql):
            raise ValueError("bad query")

    monkeypatch.setattr(routes, "get_db_manager", lambda: BadDbManager())

    response = await client.post("/api/query-and-summarize", json={"sql_query": "bad"})

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_connect_database_invalid_type(client):
    response = await client.post(
        "/api/connect-database",
        json={
            "db_type": "sqlite",
            "host": "localhost",
            "port": 1,
            "username": "u",
            "password": "p",
            "db_name": "db",
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_connect_database_success(client, monkeypatch):
    created = {}

    class FakeManager:
        def __init__(self, database_url, readonly=True):
            self.database_url = database_url
            self.readonly = readonly
            self.connected = False
            self.disconnected = False

        async def connect(self):
            self.connected = True

        async def disconnect(self):
            self.disconnected = True

    async def fake_create_session(**_kwargs):
        return "session-1"

    def fake_manager_factory(database_url, readonly=True):
        mgr = FakeManager(database_url, readonly)
        created["mgr"] = mgr
        return mgr

    monkeypatch.setattr(connection, "DatabaseManager", fake_manager_factory)
    monkeypatch.setattr(routes.chat_history, "create_session", fake_create_session)

    response = await client.post(
        "/api/connect-database",
        json={
            "db_type": "postgres",
            "host": "localhost",
            "port": 5432,
            "username": "user",
            "password": "pass",
            "db_name": "db",
            "user_id": "u1",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["session_id"] == "session-1"
    assert connection.db_manager is created["mgr"]
    assert created["mgr"].connected is True


@pytest.mark.asyncio
async def test_disconnect_database_success(client, monkeypatch):
    class FakeManager:
        def __init__(self):
            self.disconnected = False

        async def disconnect(self):
            self.disconnected = True

    closed = {"called": False}

    async def fake_close_session(_session_id):
        closed["called"] = True

    fake_manager = FakeManager()
    connection.db_manager = cast(connection.DatabaseManager, fake_manager)

    monkeypatch.setattr(routes.chat_history, "close_session", fake_close_session)

    response = await client.post("/api/disconnect-database", json={"session_id": "s-1"})

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert fake_manager.disconnected is True
    assert closed["called"] is True
    assert connection.db_manager is None


@pytest.mark.asyncio
async def test_schema_not_connected(client):
    response = await client.get("/api/schema")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "not connected"


@pytest.mark.asyncio
async def test_schema_connected(client):
    fake_manager = FakeDbManager(schema={"t": [{"column": "id", "type": "int", "nullable": False}]})
    connection.db_manager = cast(connection.DatabaseManager, fake_manager)

    response = await client.get("/api/schema")

    assert response.status_code == 200
    assert response.json()["t"][0]["column"] == "id"


@pytest.mark.asyncio
async def test_history_not_found(client, monkeypatch):
    async def fake_get_session(_session_id):
        return None

    monkeypatch.setattr(routes.chat_history, "get_session", fake_get_session)

    response = await client.get("/api/history/s-404")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_sessions(client, monkeypatch):
    async def fake_list_user_sessions(_user_id):
        return [{"session_id": "s1"}]

    monkeypatch.setattr(routes.chat_history, "list_user_sessions", fake_list_user_sessions)

    response = await client.get("/api/sessions")

    assert response.status_code == 200
    assert response.json()["sessions"][0]["session_id"] == "s1"


@pytest.mark.asyncio
async def test_get_mongo_sessions(client, monkeypatch):
    docs = [
        {
            "_id": "abc",
            "session_id": "s1",
            "user_id": "user-1",
            "db_type": "postgres",
            "db_host": "localhost",
            "db_name": "db",
            "connected_at": "now",
            "disconnected_at": None,
            "messages": [
                {
                    "role": "user",
                    "content": "hi",
                    "sql_query": None,
                    "row_count": None,
                    "timestamp": "t1",
                }
            ],
        }
    ]

    monkeypatch.setattr(routes, "get_db", lambda: FakeMongoDb(docs))

    response = await client.get("/api/mongo/sessions")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["sessions"][0]["session_id"] == "s1"
    assert body["sessions"][0]["messages"][0]["content"] == "hi"
