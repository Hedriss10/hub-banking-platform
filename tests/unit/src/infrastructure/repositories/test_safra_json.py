from src.infrastructure.repositories.helpers.safra_json import rows_from_json

pytestmark = __import__('pytest').mark.unit


def test_rows_from_json_list() -> None:
    assert rows_from_json([{'a': 1}]) == [{'a': 1}]


def test_rows_from_json_single_object() -> None:
    assert rows_from_json({'a': 1}) == [{'a': 1}]


def test_rows_from_json_none_returns_empty_list() -> None:
    assert rows_from_json(None) == []
