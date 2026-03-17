from typing import Optional, Sequence, TypeVar

T = TypeVar('T')


def get_from_sequence(
    sequence: Sequence[T] | None, index: int, default: Optional[T] = None
) -> Optional[T]:
    """
    Busca um item em uma sequência por índice,
    retornando um valor padrão se o índice não existir.
    """
    try:
        if sequence is None:
            return default
        return sequence[index]
    except (IndexError, TypeError):
        return default
