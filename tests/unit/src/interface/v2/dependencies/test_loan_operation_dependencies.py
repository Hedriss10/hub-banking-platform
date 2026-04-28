from unittest.mock import AsyncMock

import pytest
from src.interface.api.v2.controller.loan_operation import LoanOperationController
from src.interface.api.v2.dependencies.loan_operation import (
    get_loan_operation_controller,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_get_loan_operation_controller_builds_wiring() -> None:
    session = AsyncMock()
    controller = await get_loan_operation_controller(session)
    assert isinstance(controller, LoanOperationController)
