from pydantic import BaseModel


class EmployeeSituationDTO(BaseModel):
    id: int
    descricao: str
