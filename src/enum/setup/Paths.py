from enum import Enum
from src.enum.setup.City import City
import os
from src.settings.Settings import Settings

env_settings = Settings()

# Considering the current position of the file (root-->src-->state)
PROJECT_ROOT_PATH = f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..')}"
CITY = City(env_settings.CITY)

class Paths(str, Enum):
    PROJECT_ROOT_PATH = PROJECT_ROOT_PATH
    TAZ = f"{os.path.join(PROJECT_ROOT_PATH, 'data', CITY, 'net', 'taz', 'boundary')}"
    MOBILITY = f"{os.path.join(PROJECT_ROOT_PATH, 'data', CITY, 'mobility')}"
    SIM_OUTPUT = f"{os.path.join(PROJECT_ROOT_PATH, 'data', CITY, 'output')}"
    EDGE = f"{os.path.join(PROJECT_ROOT_PATH, 'data', CITY, 'net', 'edge')}"
    CENTROIDS_TAZ = f"{os.path.join(PROJECT_ROOT_PATH, 'data', CITY, 'net', 'taz', 'centroids')}"
    TAZ_EDGE = f"{os.path.join(PROJECT_ROOT_PATH, 'data', CITY, 'net', 'merge')}"
    SRC_CONFIG = f"{os.path.join(PROJECT_ROOT_PATH, 'src', 'config')}"
    SETUP_CONFIG = f"{os.path.join(PROJECT_ROOT_PATH, 'src', 'setup', 'config')}"
    NET_CONFIG = f"{os.path.join(PROJECT_ROOT_PATH, 'net_config')}"
    NET_SIMULATOR = f"{os.path.join(PROJECT_ROOT_PATH, 'data', CITY, 'net', 'sim')}"
    MOBILITY_SIMULATOR = f"{os.path.join(PROJECT_ROOT_PATH, 'data', CITY, 'mobility', 'sim')}"
    SCENARIO = f"{os.path.join(PROJECT_ROOT_PATH, 'src', 'scenario', 'planners')}"
    REPOS = f"{os.path.join(PROJECT_ROOT_PATH, 'src', 'repos')}"
    TIMELINE = f"{os.path.join(PROJECT_ROOT_PATH, 'data', CITY, 'mobility', 'timeline')}"
