from http import HTTPStatus

import pytest
from src.domain.exceptions.rooms import (
    RoomAlreadyExistsException,
    RoomNotFoundException,
)

pytestmark = pytest.mark.unit


def test_room_not_found_default() -> None:
    e = RoomNotFoundException()
    assert 'Room not found' in str(e)
    assert e.status_code == HTTPStatus.NOT_FOUND.value


def test_room_not_found_custom_message() -> None:
    e = RoomNotFoundException('Missing room')
    assert str(e) == 'Missing room'


def test_room_already_exists_default() -> None:
    e = RoomAlreadyExistsException()
    assert 'Room already exists' in str(e)
    assert e.status_code == HTTPStatus.CONFLICT.value


def test_room_already_exists_custom_message() -> None:
    e = RoomAlreadyExistsException('Name taken')
    assert str(e) == 'Name taken'
