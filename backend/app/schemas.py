"""Response contracts exposed by the API."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Machine-readable service health."""

    status: Literal["ok"]
    service: str


class ServiceInfo(BaseModel):
    """Basic navigation information for the API root."""

    name: str
    docs: str
    health: str

