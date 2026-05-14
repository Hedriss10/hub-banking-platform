from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.interface.api.v2.controller.safra import SafraController
from src.interface.api.v2.dependencies.safra import get_safra_controller

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_safra_controller_wires_layers() -> None:
    session = AsyncMock(spec=AsyncSession)
    controller = await get_safra_controller(session)
    assert isinstance(controller, SafraController)
