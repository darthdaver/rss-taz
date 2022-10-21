from enum import Enum

class Provider(str, Enum):
    BALANCE = "balance"
    BALANCES = "balances"
    SURGE_MULTIPLIER_DISTRIBUTION = "surge_multiplier_distribution"
    SURGE_MULTIPLIER = "surge_multiplier"
    SURGE_MULTIPLIERS = "surge_multipliers"
    FARE = "fare"
    REQUEST = "request"
    MAX_DRIVER_DISTANCE = "max_driver_distance"
    BASE_FARE = "base_fare"
    FEE_PER_MINUTE = "fee_per_minute"
    FEE_PER_MILE = "fee_per_mile"
