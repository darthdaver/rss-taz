from typing import TypedDict, Dict, Union
from src.enum.setup.City import City


class ScenarioRideParam(TypedDict):
    route_length_distribution: list[[float, str]]
    increment: Dict[str, float]


class ScenarioDriverParam(TypedDict):
    probability_generation: float
    personality_distribution: list[[float, str]]
    increment: Dict[str, float]


class ScenarioDriverStopWorkParam(TypedDict):
    stop_work_distribution: Dict[str, float]


class ScenarioNormalParams(TypedDict):
    city: City


class ScenarioDriverStrikeParams(TypedDict):
    city: City
    mobility_intervals: list[[float,float]]
    mobility_tazs: list[list[str]]
    simulation_intervals: list[[float,float]]
    simulation_tazs: list[list[str]]
    mobility_driver: ScenarioDriverParam
    simulation_driver: ScenarioDriverStopWorkParam


class ScenarioFlashMobParams(TypedDict):
    city: City
    simulation_intervals: list[[float, float]]
    simulation_tazs: list[list[str, list[[float, float, float], [float, float, float]]]]


class ScenarioUndergroundParams(TypedDict):
    city: City
    mobility_intervals: list[[float, float]]
    mobility_tazs: list[list[str, [float, float]]]


class ScenarioLongRidesParams(TypedDict):
    city: City
    mobility_intervals: list[[float, float]]
    mobility_tazs: list[list[str]]
    ride: ScenarioRideParam


class ScenarioProgressiveGreedyParams(TypedDict):
    city: City
    mobility_intervals: list[[float, float]]
    mobility_tazs: list[list[str]]
    driver: ScenarioDriverParam