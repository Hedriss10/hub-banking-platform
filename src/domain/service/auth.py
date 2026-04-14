from src.domain.dtos.auth import AccessTokenDTO, LoginDTO
from src.domain.exceptions.auth import InvalidCredentialsException
from src.domain.repositories.auth import AuthRepository
from src.infrastructure.utils.get_argon import verify_password
from src.infrastructure.utils.jwt_token import create_access_token


class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def login(self, login: LoginDTO) -> AccessTokenDTO:
        employee = await self.auth_repository.find_employee_by_email(login.email)
        if employee is None or not verify_password(employee.password, login.password):
            raise InvalidCredentialsException('E-mail ou senha inválidos.')

        token = create_access_token(
            employee_id=employee.id,
            email=employee.email,
            role=employee.role.value,
        )
        return AccessTokenDTO(access_token=token)
