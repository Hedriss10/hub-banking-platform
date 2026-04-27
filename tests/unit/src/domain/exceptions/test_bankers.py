from http import HTTPStatus

import pytest
from src.domain.exceptions.bankers import BankerNotFoundException

pytestmark = pytest.mark.unit


def test_banker_not_found_exception_default_message() -> None:
    e = BankerNotFoundException()
    assert 'Banker not found' in str(e)
    assert e.status_code == HTTPStatus.NOT_FOUND.value


def test_banker_not_found_exception_custom_message() -> None:
    e = BankerNotFoundException('Banco 123 inexistente')
    assert str(e) == 'Banco 123 inexistente'
