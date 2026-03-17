import pytest
from src.core.utils.get_from_sequence import get_from_sequence

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ('sequence', 'index', 'default', 'expected'),
    [
        (['a', 'b', 'c'], 1, None, 'b'),
        ((1, 2, 3), 0, None, 1),
        (['a', 'b', 'c'], -1, None, 'c'),
        (None, 0, 'default_value', 'default_value'),
        (None, 5, None, None),
        (['a'], 1, 'default', 'default'),
        (['a'], 10, None, None),
        (['a'], -2, 'default', 'default'),
        ([], 0, 'default', 'default'),
        ({1, 2, 3}, 0, 'default', 'default'),
        (['a'], 0, None, 'a'),
    ],
)
def test_get_from_sequence(sequence, index, default, expected):
    result = get_from_sequence(sequence, index, default)
    assert result == expected
