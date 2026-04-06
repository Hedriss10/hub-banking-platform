import argon2
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError

ph = PasswordHasher(
    memory_cost=65536,  # 64 MiB (padrão)
    time_cost=3,  # 3 iterações (padrão)
    parallelism=4,  # 4 threads (padrão para Argon2id)
    hash_len=32,  # 32 bytes de hash (padrão)
    salt_len=16,  # 16 bytes de salt (padrão)
)


def hash_password(password: str) -> str:
    """
    Gera um hash Argon2 seguro para a senha fornecida.

    Args:
        password: A senha em texto plano.

    Returns:
        A string completa do hash, incluindo parâmetros e salt,
        pronta para ser armazenada no banco de dados.
    """
    try:
        # O salt é gerado automaticamente.
        hashed_password = ph.hash(password)
        return hashed_password
    except argon2.exceptions.VerificationError as e:
        print(f'Erro ao gerar hash: {e}')
        raise


def verify_password(hashed_password: str, password_attempt: str) -> bool:
    """
    Verifica se a tentativa de senha corresponde ao hash armazenado.

    Args:
        hashed_password: O hash completo armazenado no banco de dados.
        password_attempt: A senha em texto plano fornecida pelo usuário.

    Returns:
        True se a senha estiver correta, False caso contrário.
    """
    try:
        ph.verify(hashed_password, password_attempt)
        return True
    except VerifyMismatchError:
        return False
    except VerificationError as e:
        print(f'Erro durante a verificação: {e}')
        return False
