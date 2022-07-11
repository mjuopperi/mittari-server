from __future__ import annotations

from datetime import datetime
from typing import Optional

from redis.client import Redis
from redis.commands.json.path import Path
from loguru import logger

from app.WSConnectionManager import WSConnectionManager
from app.util import BaseModel, generate_sensor_id


class Sensor(BaseModel):
    id: str
    created: datetime
    last_connected: datetime

    def serialize(self) -> dict:
        return {
            "id": self.id,
            "created": self.created.isoformat(),
            "last_connected": self.last_connected.isoformat(),
        }

    @staticmethod
    def deserialize(data: dict) -> Sensor:
        return Sensor(
            id=data.get("id"),
            created=datetime.fromisoformat(data.get("created")),
            last_connected=datetime.fromisoformat(data.get("last_connected")),
        )


class SensorManager:
    ws: WSConnectionManager
    redis: Redis

    def __init__(self, ws: WSConnectionManager, redis: Redis):
        self.ws = ws
        self.redis = redis

    def get_sensor(self, sensor_id: str) -> Optional[Sensor]:
        data = self.redis.json().get(sensor_id)
        logger.info(f"Found {data} for {sensor_id}")

        if data:
            return Sensor.deserialize(data)
        return None

    def save_sensor(self, sensor: Sensor):
        self.redis.json().set(sensor.id, Path.root_path(), sensor.serialize())

    def connect(self, sensor_id: Optional[str]):
        existing_sensor = self.get_sensor(sensor_id) if sensor_id else None
        if existing_sensor:
            # TODO: Change last connected
            return existing_sensor

        new_sensor = Sensor(
            id=generate_sensor_id(), created=datetime.now(), last_connected=datetime.now()
        )
        self.save_sensor(new_sensor)
        return new_sensor
