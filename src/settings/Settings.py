from pydantic import BaseSettings

class Settings(BaseSettings):
    TRACI_PORT: int
    class Config:
        env_file = '.env'