from enum import Enum
from src.enum.setup.Paths import Paths
from src.enum.setup.Dataset import Dataset
from src.enum.setup.FileFormat import FileFormat
from src.enum.setup.FileName import FileName
from src.enum.setup.City import City
import os

class FileSetup(str, Enum):
    CUSTOMER = f"{os.path.join(Paths.SRC_CONFIG, FileName.CUSTOMER)}.{FileFormat.JSON}"
    DRIVER = f"{os.path.join(Paths.SRC_CONFIG, FileName.DRIVER)}.{FileFormat.JSON}"
    SIMULATOR = f"{os.path.join(Paths.SRC_CONFIG, FileName.SIMULATOR)}.{FileFormat.JSON}"
    PROVIDER = f"{os.path.join(Paths.SRC_CONFIG, FileName.PROVIDER)}.{FileFormat.JSON}"
    SCENARIO = f"{os.path.join(Paths.SCENARIO, FileName.SCENARIO)}.{FileFormat.JSON}"
    #NET = f"{os.path.join(Paths.REPOS, 'city-mapdict-sf_n_o_minimal.json')}"
    #TAZ_EDGES = f"{os.path.join('data', 'sf_n_o_minimal_mov_edges_dict.json')}"
    NET_SUMO = f"{os.path.join(Paths.NET_CONFIG, FileName.NET_SUMO)}.{FileFormat.XML}"
    NET_SIMULATOR = f"{os.path.join(Paths.NET_SIMULATOR, FileName.NET_SIMULATOR)}.{FileFormat.JSON}"
    MOBILITY_SIMULATOR = f"{os.path.join(Paths.MOBILITY_SIMULATOR, FileName.MOBILITY_SIMULATOR)}.{FileFormat.JSON}"
    SIMULATOR_NET = f"{os.path.join(Paths.NET_CONFIG, FileName.NET_SIMULATOR)}.{FileFormat.XML}"
    PICKUPS = f"{os.path.join(Paths.MOBILITY, Dataset.SFCTA, FileFormat.JSON, City.SAN_FRANCISCO.value + '_' + Dataset.SFCTA.value + '_' + FileName.PICKUPS_STATS.value)}.{FileFormat.JSON}"
    #TIMELINE_GENERATION = f"{os.path.join(Paths.MOBILITY, FileFormat.JSON, 'timeline_gen_events_sf.json')}"
    MOBILITY_VEHICLE_TYPES = f"{os.path.join(Paths.SETUP_CONFIG, FileName.VEHICLE_TYPES)}.{FileFormat.JSON}"
    MOBILITY_RIDE = f"{os.path.join(Paths.SETUP_CONFIG, FileName.RIDE)}.{FileFormat.JSON}"
    CENTROIDS = f"{os.path.join(Paths.TAZ, FileName.RIDE)}.{FileFormat.JSON}"
    TRAVEL_TIMES = f"{os.path.join(Paths.MOBILITY, Dataset.UBER, FileFormat.JSON, City.SAN_FRANCISCO.value + '_' + Dataset.UBER.value + '_' + FileName.TRAVEL_TIME_OUT.value)}.{FileFormat.JSON}"
    TRAVEL_TIMES_MISSING_COUPLES = f"{os.path.join(Paths.MOBILITY, Dataset.UBER, FileFormat.JSON, City.SAN_FRANCISCO.value + '_' + Dataset.UBER.value + '_' + FileName.TRAVEL_TIME_MISSING_COUPLES.value)}.{FileFormat.JSON}"
    ENV = f"{os.path.join(Paths.PROJECT_ROOT_PATH, FileName.ENV)}"
    TRACI_PROVA_PROCESSES = f"{os.path.join(Paths.PROJECT_ROOT_PATH, 'prova_processes.txt')}"
