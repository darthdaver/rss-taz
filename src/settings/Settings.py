from pydantic import BaseSettings

class Settings(BaseSettings):
    TRACI_PORT: int
    DATASET_PICKUPS: str
    DATASET_TRAVEL_TIMES: str
    NET_SUMO: str
    CITY: str
    SCENARIO: str
    class Config:
        env_file = '.env'