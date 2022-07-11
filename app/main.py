from typing import Optional

import uvicorn
from fastapi import FastAPI, BackgroundTasks, Depends, Response, status
from fastapi.responses import RedirectResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import redis
from loguru import logger

from app.SensorManager import SensorManager, Sensor
from app.WSConnectionManager import WSConnectionManager
from app.util import verify_client_key, get_sensor_id_opt, get_sensor_id
from app.config import config


app = FastAPI(title="Mittari API")

r = redis.Redis(host=config.redis_host, port=config.redis_port, db=0)
TEMPERATURE_KEY = "temperature"


class Temperature(BaseModel):
    temperature: float


ws = WSConnectionManager()
sm = SensorManager(ws=ws, redis=r)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/hello", dependencies=[Depends(verify_client_key)])
def hello(sensor_id: Optional[str] = Depends(get_sensor_id_opt)):
    logger.info(f"Hello from {sensor_id}")
    sensor: Sensor = sm.connect(sensor_id)
    if not sensor_id or sensor_id != sensor.id:
        logger.info(f"New sensor connected. Assigning id {sensor.id}")
        return Response(status_code=status.HTTP_201_CREATED, content=sensor.id)
    logger.info(f"{sensor_id} connected")
    return "hello"


@app.put("/temperature", dependencies=[Depends(verify_client_key)])
async def put_temperature(
    temperature: Temperature,
    background_tasks: BackgroundTasks,
    sensor_id: str = Depends(get_sensor_id),
):
    background_tasks.add_task(ws.broadcast, str(temperature.temperature))
    logger.info(f"Temperature from {sensor_id}: {temperature.temperature}")
    return {"status": "ok"}


@app.get("/temperature", response_model=Temperature)
def get_temperature(sensor_id: str):
    temperature = r.get(f"{TEMPERATURE_KEY}.{sensor_id}")
    return {"temperature": float(temperature) if temperature else None}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws.disconnect(websocket)


def startup_check():
    try:
        if not r.ping():
            logger.error("Could not connect to Redis")
            exit(1)
    except redis.ConnectionError:
        logger.error("Could not connect to Redis")
        exit(1)


def start():
    startup_check()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start()
