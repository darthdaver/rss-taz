from pydantic import BaseSettings
import os

PROJECT_ROOT_PATH = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')}"

class Settings(BaseSettings):
    TRACI_PORT: int
    DATASET_PICKUPS: str
    DATASET_TRAVEL_TIMES: str
    NET_SUMO: str
    CITY: str
    SCENARIO: str

    class Config:
        env_file = f"{PROJECT_ROOT_PATH}/.env"