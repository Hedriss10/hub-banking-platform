from abc import ABC, abstractmethod
from typing import Optional

from src.domain.dtos.employee import EmployeeDTO


class AuthRepository(ABC):
    @abstractmethod
    async def find_employee_by_email(self, email: str) -> Optional[EmployeeDTO]:
        """
        Busca funcionário pelo e-mail (inclui o hash da senha no DTO).

        A conferência da senha em texto plano fica no domínio (`AuthService`),
        com Argon2 — não no SQL.
        """
        ...
