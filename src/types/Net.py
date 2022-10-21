from typing import TypedDict
from src.types.Human import PersonalityDistribution


class Centroids(TypedDict):
    taz_id: str
    coordinates: list[float, float]

class TazDistance(TypedDict):
    short: list[str]
    normal: list[str]
    long: list[str]
    extreme: list[str]

class TazInfo(TypedDict):
    id: str
    personality_distribution: PersonalityDistribution
    balances: list[int]
    surge_multipliers: list[int]
    started: int
    ended: int
    requested: int
    rejected: int
    canceled: int
    unserved: int
    edges: list[str]
    distance: TazDistance

class EdgeInfo(TypedDict):
    id: str
    taz_id: str
    length: float
    speed: float

class NetDataset(TypedDict):
    taz: dict[str, TazInfo]  # { str: TazInfo }
    edges: dict[str, EdgeInfo]  # { str: EdgeInfo }

class Net(TypedDict):
    boundary: NetDataset
    mobility: NetDataset
    analytics: NetDataset

