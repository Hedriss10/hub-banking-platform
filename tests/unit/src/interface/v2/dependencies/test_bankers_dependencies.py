from unittest.mock import AsyncMock

import pytest
from src.interface.api.v2.controller.bankers import BankersController
from src.interface.api.v2.dependencies.bankers import get_bankers_controller

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_bankers_controller_builds_wiring() -> None:
    session = AsyncMock()
    controller = await get_bankers_controller(session)
    assert isinstance(controller, BankersController)
