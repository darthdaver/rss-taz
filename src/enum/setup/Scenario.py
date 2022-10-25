from enum import Enum

class Scenario(str, Enum):
    NORMAL = "normal"
    GREEDY = "greedy"
    DRIVER_STRIKE = "driver_strike"
    LONG_RIDES = "long_rides"