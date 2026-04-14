from src.domain.dtos.auth import AccessTokenDTO, LoginDTO
from src.domain.service.auth import AuthService


class AuthUseCase:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    async def login(self, login: LoginDTO) -> AccessTokenDTO:
        return await self.auth_service.login(login)
