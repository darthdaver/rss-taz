from typing import TypedDict
from src.types.Human import HumanInfo
from src.types.Route import RouteInfo
from src.enum.types.PersonalityType import PersonalityType as PersonalityType
from src.enum.state.DriverState import DriverState
from src.enum.state.CustomerState import CustomerState


class DriverInfo(HumanInfo):
    route: RouteInfo
    last_ride_timestamp: float
    rides_completed: int
    current_edge_id: str
