from enum import Enum

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
    NET_SUMO = 'san-francisco.net'
    # SCENARIOS
    SCENARIO = 'normal'
    ENV = ".env"

