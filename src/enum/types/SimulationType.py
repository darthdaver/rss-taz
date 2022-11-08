from enum import Enum

class SimulationType(str, Enum):
    NORMAL = "normal"
    PEAK = "PEAK"
    GREEDY = "greedy"