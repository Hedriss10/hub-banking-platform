from pydantic import BaseModel


class LoginRequestSchema(BaseModel):
    email: str
    password: str


class LoginResponseSchema(BaseModel):
    access_token: str
    token_type: str = 'bearer'
