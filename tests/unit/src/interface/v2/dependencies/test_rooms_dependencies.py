from unittest.mock import AsyncMock

import pytest
from src.interface.api.v2.controller.rooms import RoomsController
from src.interface.api.v2.dependencies.rooms import get_rooms_controller

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_rooms_controller_builds_wiring() -> None:
    session = AsyncMock()
    controller = await get_rooms_controller(session)
    assert isinstance(controller, RoomsController)
