from typing import TypedDict, Dict
from src.types.Net import TazInfo
from src.types.Ride import RideStats


class SimulatorPerformanceRow(TypedDict):
    customer_generation: float
    driver_generation: float
    check_driver_list: float
    check_customer_list: float
    customer_requests: float
    processed_rides: float
    managed_pending_requests: float
    updated_surge_multiplier: float
    updated_drivers: float
    updated_ride_states: float
    updated_driver_movements: float


class GlobalIndicatorsInfo(TypedDict):
    requested: int
    canceled: int
    accepted: int
    not_served: int
    rejections: float
    tazs_stats: Dict[str, Dict[str,TazInfo]]


class SpecificIndicatorsInfo(TypedDict):
    ride_stats: list[RideStats]


class DriverStatsInfo(TypedDict):
    id: str
    start_timestamp: float
    ride_ids_list: list[str]
    moving_to_tazs_list: list[[float,str,str]]
    remotion_timestamp: float
    remotion_reason: str