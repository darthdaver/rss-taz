from enum import Enum

class Scenario(str, Enum):
    NORMAL = "normal"
    PROGRESSIVE_GREEDY = "progressive_greedy"
    DRIVER_STRIKE = "driver_strike"
    LONG_RIDES = "long_rides"
    FLASH_MOB = "flash_mob"
    UNDERGROUND = "underground"