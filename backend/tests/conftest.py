import pytest
from httpx import ASGITransport, AsyncClient

from app.api import routes
from app.auth.entra import validate_token
from app.cache import semantic_qa_cache
from app.database import connection
from main import app


@pytest.fixture
def app_instance():
    app.dependency_overrides[validate_token] = lambda: {"sub": "user-1"}
    yield app
    app.dependency_overrides = {}


@pytest.fixture
async def client(app_instance):
    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


@pytest.fixture(autouse=True)
def reset_db_manager():
    connection.db_manager = None
    yield
    connection.db_manager = None


@pytest.fixture(autouse=True)
def patch_infrastructure(monkeypatch):
    """Patching Redis, MongoDB and semantic cache for all tests automatically"""

    # Redis
    async def fake_get_json(_key):
        return None

    async def fake_set_json(_key, _val, **_kw):
        return True

    async def fake_incr(_key, _amount=1):
        return 1

    monkeypatch.setattr(routes.redis_client, "get_json", fake_get_json)
    monkeypatch.setattr(routes.redis_client, "set_json", fake_set_json)
    monkeypatch.setattr(routes.redis_client, "incr", fake_incr)

    # MongoDB chat history
    async def fake_get_session(_session_id):
        return None

    async def fake_add_message(**_kwargs):
        pass

    monkeypatch.setattr(routes.chat_history, "get_session", fake_get_session)
    monkeypatch.setattr(routes.chat_history, "add_message", fake_add_message)

    # Semantic cache
    async def fake_probe(_db_fp, _question):
        return semantic_qa_cache.SemanticQACacheProbe(hit=None, best_similarity=None, best_entry_id=None)

    async def fake_store(**_kwargs):
        pass

    monkeypatch.setattr(semantic_qa_cache, "probe_similar_answer", fake_probe)
    monkeypatch.setattr(semantic_qa_cache, "store_answer", fake_store)