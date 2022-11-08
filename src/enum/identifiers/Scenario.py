from enum import Enum


class Scenario(str, Enum):
    NAME = "name"
    PARAMS = "params"
    TAZ = "taz"
    ID = "id"
    CUSTOMER = "customer"
    DRIVER = "driver"
    RIDE = "ride"
    MOBILITY_PLANNER = "mobility_planner"
    SIMULATION_PLANNER = "simulation_planner"
    BEGIN = "begin"
    END = "end"
    EVENT_TYPE = "type"
    SLOW_DOWN = "slow_down"
    SPEED_UP = "speed_up"
    RATE = "rate"
    INTERVAL = "interval"
    REQUESTS = "requests"
    INCREMENT = "increment"
    UNIFORM_DISTRIBUTION = "uniform_distribution"
    CITY = "city"
    MOBILITY_INTERVALS = "mobility_intervals"
    MOBILITY_TAZS = "mobility_tazs"
    SIMULATION_INTERVALS = "simulation_intervals"
    SIMULATION_TAZS = "simulation_tazs"
    MOBILITY_DRIVER = "mobility_driver"
    SIMULATION_DRIVER = "simulation_driver"
    SPEED_TYPE = "speed_type"


