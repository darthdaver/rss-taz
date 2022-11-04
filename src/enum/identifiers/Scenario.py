from enum import Enum


class Scenario(str, Enum):
    NAME = "name"
    PARAMS = "params"
    TAZ = "taz"
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


