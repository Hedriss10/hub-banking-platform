from enum import Enum


class DocumentType(Enum):
    CPF = 'CPF'
    CNPJ = 'CNPJ'
    RG = 'RG'
    CNH = 'CNH'
    PASSPORT = 'PASSPORT'
    DRIVER_LICENSE = 'DRIVER_LICENSE'
    OTHER = 'OTHER'
