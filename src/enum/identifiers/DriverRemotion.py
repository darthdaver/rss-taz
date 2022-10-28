from enum import Enum

class DriverRemotion(str, Enum):
    SET_ROUTE_FAILED = "set_route_failed"
    TRACI_FORCED_REMOTION = "traci_forced_remotion"
    STOP_WORK = "stop_work"