import pytest
from src.infrastructure.repositories.helpers.serializer_json import _json_to_banker_rows

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ('payload', 'expected_len'),
    [
        ([{'a': 1}, {'b': 2}], 2),
        ([1, {'x': 1}], 1),
        ({'data': [{'x': 1}]}, 1),
        ({'bancos': [{'y': 2}]}, 1),
        ({'items': [{'z': 3}]}, 1),
        ({'result': [{'w': 4}]}, 1),
        ({'other': []}, 0),
        ({}, 0),
        ('not-a-list', 0),
    ],
)
def test_json_to_banker_rows(payload, expected_len: int) -> None:
    rows = _json_to_banker_rows(payload)
    assert len(rows) == expected_len
