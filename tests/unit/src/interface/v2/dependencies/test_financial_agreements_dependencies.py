from unittest.mock import AsyncMock

import pytest
from src.interface.api.v2.controller.financial_agreements import (
    FinancialAgreementsController,
)
from src.interface.api.v2.dependencies.financial_agreements import (
    get_financial_agreements_controller,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_financial_agreements_controller_builds_wiring() -> None:
    session = AsyncMock()
    controller = await get_financial_agreements_controller(session)
    assert isinstance(controller, FinancialAgreementsController)
