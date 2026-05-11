from unittest.mock import AsyncMock

import pytest
from src.interface.api.v2.controller.proposal import ProposalController
from src.interface.api.v2.dependencies.proposal import get_proposal_controller

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_proposal_controller_returns_controller() -> None:
    session = AsyncMock()
    ctrl = await get_proposal_controller(session)
    assert isinstance(ctrl, ProposalController)
