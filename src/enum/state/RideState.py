from enum import Enum

class RideState(str, Enum):
    # Simulation
    REQUESTED = "REQUESTED"
    PENDING = "PENDING"
    PICKUP = "PICKUP"
    ON_ROAD = "ON_ROAD"
    END = "END"
    CANCELED = "CANCELED"
    NOT_SERVED = "NOT SERVED"
    SIMULATION_ERROR = "SIMULATION ERROR"
