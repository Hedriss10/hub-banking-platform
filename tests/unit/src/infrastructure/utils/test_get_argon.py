from unittest.mock import MagicMock, patch

import pytest
from argon2.exceptions import VerificationError
from src.infrastructure.utils.get_argon import hash_password, verify_password


@pytest.mark.parametrize(
    'password',
    [
        'strongpassword123',
        'short',
        'with_special_chars!@#',
        '',
    ],
)
def test_hash_password_success(password):
    hashed = hash_password(password)

    assert isinstance(hashed, str)
    assert hashed.startswith('$argon2id$')
    assert verify_password(hashed, password) is True


def test_hash_password_verification_error():
    mock_ph = MagicMock()
    mock_ph.hash.side_effect = VerificationError('Simulated error')
    with patch('src.infrastructure.utils.get_argon.ph', mock_ph):
        with pytest.raises(VerificationError, match='Simulated error'):
            hash_password('testpass')


@pytest.mark.parametrize(
    ('password', 'attempt', 'expected'),
    [
        ('correctpass', 'correctpass', True),
        ('correctpass', 'wrongpass', False),
        ('correctpass', '', False),
        ('', '', True),
    ],
)
def test_verify_password(password, attempt, expected):
    hashed = hash_password(password)

    result = verify_password(hashed, attempt)
    assert result == expected


def test_verify_password_mismatch_error():
    hashed = hash_password('correct')
    result = verify_password(hashed, 'wrong')
    assert result is False


def test_verify_password_verification_error_with_print():
    mock_ph = MagicMock()
    mock_ph.verify.side_effect = VerificationError('Simulated verify error')
    with patch('src.infrastructure.utils.get_argon.ph', mock_ph):
        with patch('builtins.print') as mock_print:
            # Act
            result = verify_password('dummy_hash', 'test')

            # Assert
            assert result is False
            mock_print.assert_called_once_with(
                'Erro durante a verificação: Simulated verify error'
            )
