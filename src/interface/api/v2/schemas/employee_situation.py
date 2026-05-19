from pydantic import BaseModel


class EmployeeSituationSchema(BaseModel):
    id: int
    descricao: str
