from enum import Enum


class SafraBpoProducts(Enum):
    """
    Produto que será
    Capturada a proposta.
    1 - NOVO 2 - REFIN 5 - RETENÇÃO 7 - PORTABILIDADE
    """

    NOVO = 1
    REFIN = 2
    RETENCAO = 5
    PORTABILIDADE = 7
