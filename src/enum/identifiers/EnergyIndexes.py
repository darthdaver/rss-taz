from enum import Enum

class EnergyIndexes(str, Enum):
    REQUESTED = "requested"
    CANCELED = "canceled"
    ACCEPTED = "accepted"
    NOT_SERVED = "not_served"
    OVERHEAD = "overhead"
    PRICE_FLUCTUATION = "price_fluctuation"
