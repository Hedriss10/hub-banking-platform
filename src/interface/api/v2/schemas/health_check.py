from typing import Literal, Optional

from pydantic import BaseModel

HealthStatus = Literal['healthy', 'unhealthy']


class ComponentHealthSchema(BaseModel):
    status: HealthStatus
    detail: Optional[str] = None


class HealthChecksSchema(BaseModel):
    application: ComponentHealthSchema
    database: ComponentHealthSchema
    redis: ComponentHealthSchema


class HealthCheckResponseSchema(BaseModel):
    status: HealthStatus
    app_name: str
    version: str
    checks: HealthChecksSchema
