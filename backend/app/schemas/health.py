from typing import Literal

from pydantic import BaseModel

HealthStatus = Literal["ok", "error"]
OverallStatus = Literal["ok", "degraded"]


class HealthResponse(BaseModel):
    status: OverallStatus
    postgres: HealthStatus
    redis: HealthStatus
