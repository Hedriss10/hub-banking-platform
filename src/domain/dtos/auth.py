from pydantic import BaseModel


class LoginDTO(BaseModel):
    email: str
    password: str


class AccessTokenDTO(BaseModel):
    access_token: str
    token_type: str = 'bearer'
