import pytest
from src.interface.api.v2.controller.auth import AuthController
from src.interface.api.v2.dependencies.auth import get_auth_controller

pytestmark = pytest.mark.unit


class DummySession:
    pass


@pytest.mark.asyncio
async def test_get_auth_controller_returns_instance() -> None:
    controller = await get_auth_controller(DummySession())
    assert isinstance(controller, AuthController)
