from typing import TypedDict, Dict


class FareSetup(TypedDict):
    base_fare: float
    minimum_fare: float
    fee_per_minute: float
    fee_per_mile: float
    surge_multiplier_distribution: list[[float, float, float]]


class RequestSetup(TypedDict):
    max_driver_distance: float


class ProviderSetup(TypedDict):
    fare: FareSetup
    request: RequestSetup


class DriverSetup(TypedDict):
    move_distribution: Dict[str,list[[float, float, float]]]
    personality_distribution: list[[float, str]]
    acceptance_distribution: Dict[str, list[float, float, float]]
    stop_work_distribution: Dict[str, float]


class CustomerSetup(TypedDict):
    personality_distribution: list[[float, str]]
    acceptance_distribution: Dict[str, list[float, float, float]]
