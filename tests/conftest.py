import uuid
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    with TestClient(app=app, base_url='http://test') as c:
        yield c


@pytest.fixture
def generate_uuid() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_repository_user():
    repo = AsyncMock()
    return repo
