import uuid
from typing import Optional

from fastapi import Header, HTTPException
from pydantic import BaseModel as PydanticBaseModel

from app.config import config


async def verify_client_key(x_client_key: str = Header(None)):
    if x_client_key != config.client_key:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def get_sensor_id(x_sensor_id: str = Header(None)) -> str:
    if not x_sensor_id:
        raise HTTPException(status_code=400, detail="Sensor ID missing")
    return x_sensor_id


async def get_sensor_id_opt(x_sensor_id: str = Header(None)) -> Optional[str]:
    return x_sensor_id


def generate_sensor_id() -> str:
    return str(uuid.uuid4())


def to_camel(field: str) -> str:
    head, *tail = field.split("_")
    return head + "".join([part.capitalize() for part in tail])


class BaseModel(PydanticBaseModel):
    class Config:
        allow_population_by_field_name = True
        alias_generator = to_camel
