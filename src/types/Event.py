from typing import TypedDict


class EventInfo(TypedDict):
    requested: int
    canceled: int
    accepted: int
    not_served: int
    overhead: float
    price_fluctuation: float