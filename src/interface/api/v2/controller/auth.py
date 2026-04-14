from src.domain.dtos.auth import LoginDTO
from src.domain.use_case.auth import AuthUseCase
from src.interface.api.v2.schemas.auth import LoginRequestSchema, LoginResponseSchema


class AuthController:
    def __init__(self, auth_use_case: AuthUseCase):
        self.auth_use_case = auth_use_case

    async def login(self, login: LoginRequestSchema) -> LoginResponseSchema:
        dto = LoginDTO.model_validate(login.model_dump())
        result = await self.auth_use_case.login(dto)
        return LoginResponseSchema.model_validate(result.model_dump())
