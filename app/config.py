import os
from dataclasses import dataclass

import dotenv


@dataclass
class Config:
    redis_host: str
    redis_port: int
    client_key: str


dotenv.load_dotenv()
config = Config(
    redis_host=os.getenv("REDIS_HOST"),
    redis_port=int(os.getenv("REDIS_PORT")),
    client_key=os.getenv("CLIENT_KEY"),
)
