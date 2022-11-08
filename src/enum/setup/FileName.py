from enum import Enum

from src.enum.setup.City import City
from src.enum.setup.Scenario import Scenario
from src.settings.Settings import Settings

env_settings = Settings()
NET_SUMO = env_settings.NET_SUMO
CITY = City(env_settings.CITY)
SCENARIO_SETTING = Scenario(env_settings.SCENARIO)

class FileName(str, Enum):
    PICKUPS_DROPOFFS = 'pickups_dropoffs'
    PICKUPS_STATS = 'pickups_stats'
    DROP_STATS = 'dropoffs_stats'
    TAZ_BOUNDARY = 'taz_boundary'
    TAZ_POLY_SUMO = 'taz_poly.poi'
    TAZ_POLY_DICT = 'taz_poly_dict'
    TAZ_EDGE = 'taz_edge'
    TAZ_EDGE_DICT = 'taz_edge_dict'
    TAZ_TIMELINE_DICT = 'taz_timeline_dict'
    EDGE_DISTRICTS = 'edges_districts.poi'
    EDGE_DISTRICTS_DICT = 'edges_districts_dict'
    MOBILITY = 'mobility'
    CENTROIDS = 'taz_centroids'
    TRAVEL_TIME_CONCAT_MEAN = 'travel_time_concat_mean'
    TRAVEL_TIME_MISSING_COUPLES = 'travel_time_missing_couples'
    TRAVEL_TIME_IN = 'travel_time_Q4_2019'
    TRAVEL_TIME_OUT = 'travel_time'
    EDGE_SPEED = 'speed_Q4_2018'
    TIMELINE_DICT = 'timeline_dict'
    VEHICLE_TYPES = 'vehicle_types'
    NET_SIMULATOR = 'net_simulator'
    MOBILITY_SIMULATOR = 'mobility_simulator'
    # SETUP
    RIDE = 'ride'
    CUSTOMER = 'customer'
    DRIVER = 'driver'
    SIMULATOR = 'simulator'
    PROVIDER = 'provider'
    NET_SUMO = NET_SUMO
    # SCENARIOS
    SCENARIO = f"{CITY.value}_{SCENARIO_SETTING.value}_planner"
    SCENARIO_CONFIG = f"{CITY.value}_{SCENARIO_SETTING.value}_config"
    SCENARIO_PLANNER = f"planner"
    ENV = ".env"
    ENERGY_INDEXES_100 = "energy_indexes_100"
    ENERGY_INDEXES_200 = "energy_indexes_200"
    ENERGY_INDEXES_500 = "energy_indexes_500"
    ENERGY_INDEXES_100_VALUES = "energy_indexes_100_values"
    ENERGY_INDEXES_200_VALUES = "energy_indexes_200_values"
    ENERGY_INDEXES_500_VALUES = "energy_indexes_500_values"
    ENERGY_INDEXES = "energy_indexes"
    GLOBAL_INDICATORS = "global_indicators"
    SPECIFIC_INDICATORS = "specific_indicators"
    SIMULATOR_PERFORMANCES = "simulator_performances"
    DRIVERS_STATS = "drivers_stats"
    RIDES_STATS = "rides_stats"


