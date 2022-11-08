from enum import Enum
from src.enum.setup.Paths import Paths
from src.enum.setup.Dataset import Dataset
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.City import City
from src.enum.setup.Scenario import Scenario
from src.settings.Settings import Settings
import os

env_settings = Settings()

CITY = City(env_settings.CITY)
DATASET_PICKUPS = Dataset(env_settings.DATASET_PICKUPS)
DATASET_TRAVEL_TIMES = Dataset(env_settings.DATASET_TRAVEL_TIMES)
SCENARIO_SETTING = Scenario(env_settings.SCENARIO)

class FileSetup(str, Enum):
    CUSTOMER = f"{os.path.join(Paths.SETUP_CONFIG, FileName.CUSTOMER)}.{FileFormat.JSON}"
    DRIVER = f"{os.path.join(Paths.SETUP_CONFIG, FileName.DRIVER)}.{FileFormat.JSON}"
    SIMULATOR = f"{os.path.join(Paths.SETUP_CONFIG, FileName.SIMULATOR)}.{FileFormat.JSON}"
    PROVIDER = f"{os.path.join(Paths.SETUP_CONFIG, FileName.PROVIDER)}.{FileFormat.JSON}"
    SCENARIO = f"{os.path.join(Paths.SCENARIO, SCENARIO_SETTING, FileFormat.JSON, FileName.SCENARIO)}.{FileFormat.JSON}"
    #NET = f"{os.path.join(Paths.REPOS, 'city-mapdict-sf_n_o_minimal.json')}"
    #TAZ_EDGES = f"{os.path.join('data', 'sf_n_o_minimal_mov_edges_dict.json')}"
    NET_SUMO = f"{os.path.join(Paths.NET_CONFIG, FileName.NET_SUMO)}.{FileFormat.XML}"
    NET_SIMULATOR = f"{os.path.join(Paths.NET_SIMULATOR, FileFormat.JSON, FileName.NET_SIMULATOR)}.{FileFormat.JSON}"
    MOBILITY_SIMULATOR = f"{os.path.join(Paths.MOBILITY_SIMULATOR, FileFormat.JSON, FileName.MOBILITY_SIMULATOR)}.{FileFormat.JSON}"
    PICKUPS = f"{os.path.join(Paths.MOBILITY, DATASET_PICKUPS.value, FileFormat.JSON, CITY.value + '_' + DATASET_PICKUPS.value + '_' + FileName.PICKUPS_STATS.value)}.{FileFormat.JSON}"
    #TIMELINE_GENERATION = f"{os.path.join(Paths.MOBILITY, FileFormat.JSON, 'timeline_gen_events_sf.json')}"
    MOBILITY_VEHICLE_TYPES = f"{os.path.join(Paths.SETUP_CONFIG, FileName.VEHICLE_TYPES)}.{FileFormat.JSON}"
    RIDE = f"{os.path.join(Paths.SETUP_CONFIG, FileName.RIDE)}.{FileFormat.JSON}"
    CENTROIDS = f"{os.path.join(Paths.TAZ, FileName.RIDE)}.{FileFormat.JSON}"
    TRAVEL_TIMES = f"{os.path.join(Paths.MOBILITY, DATASET_TRAVEL_TIMES.value, FileFormat.JSON, CITY.value + '_' + DATASET_TRAVEL_TIMES.value+ '_' + FileName.TRAVEL_TIME_OUT.value)}.{FileFormat.JSON}"
    TRAVEL_TIMES_MISSING_COUPLES = f"{os.path.join(Paths.MOBILITY, DATASET_TRAVEL_TIMES.value, FileFormat.JSON, CITY.value + '_' + DATASET_TRAVEL_TIMES.value + '_' + FileName.TRAVEL_TIME_MISSING_COUPLES.value)}.{FileFormat.JSON}"
    ENV = f"{os.path.join(Paths.PROJECT_ROOT_PATH, FileName.ENV)}"
    TRACI_PROVA_PROCESSES = f"{os.path.join(Paths.PROJECT_ROOT_PATH, 'prova_processes.txt')}"
    SCENARIO_CONFIG = f"{os.path.join(Paths.SCENARIO, SCENARIO_SETTING, FileFormat.JSON, FileName.SCENARIO_CONFIG)}.{FileFormat.JSON}"