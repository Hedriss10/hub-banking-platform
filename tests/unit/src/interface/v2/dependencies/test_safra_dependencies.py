import pytest
from src.interface.api.v2.controller.safra import SafraController
from src.interface.api.v2.dependencies.safra import get_safra_controller

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_safra_controller_wires_layers() -> None:
    controller = await get_safra_controller()
    assert isinstance(controller, SafraController)
