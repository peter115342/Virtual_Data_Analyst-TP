import pytest
from httpx import ASGITransport, AsyncClient

from app.auth.entra import validate_token
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
